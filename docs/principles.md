# Principles

Source Cut exists to make one kind of film: a short documentary where the viewer can check every claim. These rules
come from making eighteen of them. Every tool in this repository is built to make them easy to follow.

## 1. Every claim is on screen

When the narrator says a number, a date or a quote, the viewer sees the document it came from: a filing, a letter, a
press release, an article, a court record. The document sits on a card, and a marker sweeps across the exact words as
they are spoken. If you cannot show where a claim came from, cut the claim.

## 2. Real pictures only

- Footage is real footage from the period: interviews, keynotes, news reports, archive film. Cut short quotes, credit
  them on screen, and link them in the description.
- Photographs come from Wikimedia Commons or another source whose licence you have checked. Every photo gets a credit
  line on screen and in the description.
- No stock footage. A generic office or a stock "businessman" tells the viewer nothing and costs trust.
- No AI-generated people presented as real. If an image model touches a real person (for example in a thumbnail), say
  so in the upload notes and compare it with the source photo before you ship it.

## 3. Attribute every characterisation

If a person is described as reckless, visionary or anything in between, the words belong to a named outlet or
document, on screen. The narrator states facts; opinions are quoted with their source.

## 4. The thumbnail is a promise

A thumbnail must be true, and the film must deliver it within the first minute. YouTube's A/B test picks the variant
with the most watch time, not the most clicks, so a misleading thumbnail loses anyway.

Image models invent things: headlines in the background, extra aircraft, logos, a new face. Review every generated
image against its sources before it ships.

## 5. Every number has a source line

Each film keeps a `RESEARCH.md` with a source for every fact, and its upload description lists the sources and
credits. Where sources disagree (one says 143 days, another 145), say so in the description.

## 6. Quality does not drop in a batch

When you make five films in a week, each one still gets the same facts check, the same contact-sheet review and the
same loudness check. The tools make those checks cheap so there is no excuse to skip them.

## 7. Nothing heavy runs on your laptop

Rendering, encoding and image generation run on a cloud VM inside Docker. Your laptop writes scripts and reviews
contact sheets. This keeps renders reproducible and stops the laptop from freezing halfway through a film.
