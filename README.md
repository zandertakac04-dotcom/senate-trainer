# Senator Face Memory Trainer

A browser-based typed-answer learner for all 100 U.S. senators serving on October 28, 2026. Each question shows a real portrait and asks for the senator's name and state. The checker accepts small spelling errors and optional middle names; wrong answers immediately reveal the correct name and state and can be followed by the next question.

## How it works

- Practice 10, all 100, alphabetical order, or review previously missed senators.
- Saves learning progress and review flags in the browser.
- Downloads congressional portraits during the GitHub Actions build and serves the image files from this site. The quiz does not rely on external photo URLs while you study.
- The build validates the full set and fails rather than publish if any portrait is missing.

## Publishing

Repository: https://github.com/zandertakac04-dotcom/senate-trainer

A push to `main` runs `.github/workflows/deploy-pages.yml`. The workflow enables GitHub Pages, downloads and validates the 100 portrait files, builds the site, and deploys it. When the run succeeds, the site URL is:

https://zandertakac04-dotcom.github.io/senate-trainer/

You can check build results under the repository's **Actions** tab.

## Data and portrait sources

- Official Senate roster: https://www.senate.gov/senators/index.htm
- Congress-legislators public member dataset: https://github.com/unitedstates/congress-legislators
- Images of Congress archive: https://github.com/unitedstates/images

The images archive documents its congressional portraits as public domain in the United States. A few recently appointed senators' portraits are served from specific Wikimedia Commons versions of official public-domain portraits when the main archive does not yet contain them.

The roster is a dated snapshot for October 28, 2026. Check the official Senate list and rebuild/update the roster if membership changes.
