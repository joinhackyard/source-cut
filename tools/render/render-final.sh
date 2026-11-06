#!/bin/sh
# Runs ON the render VM: delivery render of a film (4 chunks, 2 at a time) and its Short, then join and loudness-normalise.
#   copy to the VM, then:  nohup ./render-final.sh <remote project dir> <film end seconds> <tag> &
#   finished when /tmp/<tag>-done exists; logs in /tmp/<tag>-*.log
# Queue renders back to back so two never compete for the CPU:
#   nohup sh -c "while [ ! -f /tmp/prev-done ]; do sleep 20; done; ./render-final.sh ..." &
P=$(realpath "$1"); END=$2; T=$3; C=$(dirname "$P")/.cache
mkdir -p "$C"; rm -f /tmp/$T-done
R(){ docker run --rm -v $P/$1:/work -v $C:/root/.cache hyperframes-runner hyperframes render --quality delivery --workers 12 \
     --start $2 --end $3 --output renders/$4.mp4 > /tmp/$T-$4.log 2>&1; }
Q=$(python3 -c "e=$END;print(round(e/4,2),round(e/2,2),round(3*e/4,2))")
set -- $Q
R film 0 $1 c1 & R film $1 $2 c2 & wait
R film $2 $3 c3 & R film $3 $END c4 & wait
docker run --rm -v $P/short:/work -v $C:/root/.cache hyperframes-runner hyperframes render --quality delivery --workers 16 \
  --output renders/final-raw.mp4 > /tmp/$T-short.log 2>&1
docker run --rm -v $P:/p -w /p hyperframes-runner sh -c "chown -R $(id -u):$(id -g) /p/film/renders /p/short/renders; \
  cd film/renders && printf 'file c1.mp4\nfile c2.mp4\nfile c3.mp4\nfile c4.mp4\n' > l.txt && \
  ffmpeg -v error -y -f concat -safe 0 -i l.txt -c copy joined.mp4; \
  cd /p/short/renders && cp final-raw.mp4 joined.mp4"
echo "rendered; now run tools/render/loudness.sh on film/renders/joined.mp4 and short/renders/joined.mp4"
echo done > /tmp/$T-done
