# Senator Face Memory Trainer

A browser-based typed-answer learner for all 100 U.S. senators serving on October 28, 2026. Each question shows a real portrait and asks for the senator's name and state. The checker accepts small spelling errors and optional middle names; wrong answers immediately reveal the correct name and state and let you move on.

## Features

- Practice 10, all 100, alphabetical order, or review previously missed senators.
- Saves learning progress and review flags in your browser.
- Downloads congressional portraits during the build and serves the image files from this website. Quiz-time photos are not loaded from third-party URLs.
- The build validates the full set and fails rather than publish if any portrait is missing.

## One-time setup and publishing

Repository: https://github.com/zandertakac04-dotcom/senate-trainer

1. Open [Repository Settings → Pages](https://github.com/zandertakac04-dotcom/senate-trainer/settings/pages).
2. Under **Build and deployment**, choose **GitHub Actions** as the source, then save if prompted.
3. Open the repository's **Actions** tab and run **Build and deploy Senator Face Memory Trainer**, or make a push to `main`.
4. The workflow downloads and validates all 100 portraits, bundles them, and deploys the site. A successful build must report `BUILD SUCCESS: exactly 100 senator portraits downloaded, validated, and bundled`.
5. Open https://zandertakac04-dotcom.github.io/senate-trainer/

If the build fails, open its run and inspect the **Download and validate all 100 portraits** step. The workflow deliberately refuses to publish a site with a missing picture.

## Sources

- Official Senate roster: https://www.senate.gov/senators/index.htm
- Congress-legislators public member dataset: https://github.com/unitedstates/congress-legislators
- Images of Congress archive: https://github.com/unitedstates/images

The images archive documents its congressional portraits as public domain in the United States. Portraits for a few recently appointed senators are drawn from specific, identified public-domain official portraits where the archive does not yet contain an image.

The roster is a dated snapshot for October 28, 2026. Check the official Senate list and update the roster if membership changes.
