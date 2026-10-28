# Senator Face Memory Trainer

A browser-based typing quiz for all 100 U.S. senators serving on October 28, 2026. Each question shows a real portrait and asks for the senator's name and state. Common small spelling mistakes are accepted. When an answer is wrong, the trainer immediately reveals the correct answer and lets you continue.

## Publish the website

The GitHub Actions workflow downloads each senator's portrait from the United States Images of Congress archive, using the member's Bioguide ID from the public congress-legislators dataset. It validates that all 100 real portraits downloaded before deploying, then bundles the image files with the site so quiz-time photos are same-site files.

1. In the repository settings, open **Settings → Pages**.
2. Set **Build and deployment → Source** to **GitHub Actions**.
3. Open **Actions** and select **Build and deploy Senator Face Memory Trainer**.
4. Run the workflow (or push a commit). It refuses to deploy if any portrait is missing.
5. When the workflow succeeds, use the website URL shown in the Pages deployment.

Portrait source: https://github.com/unitedstates/images (public-domain congressional portraits).
Member ID data: https://github.com/unitedstates/congress-legislators
Official roster: https://www.senate.gov/senators/index.htm

The roster is a dated snapshot (October 28, 2026); it should be checked and refreshed when membership changes.
