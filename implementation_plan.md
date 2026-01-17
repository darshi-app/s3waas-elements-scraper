# S3WaaS Notice & Content Scraper Plan

## Goal
Extract structured text content and associated documents (PDFs) from specific sections (Notices, Tenders, Recruitments, What's New) of S3WaaS government websites. Ignore generic theme assets (logos, banners). **Resolve intermediate links to finding actual PDF URLs.**

## User Review Required
> [!IMPORTANT]
> This scraper relies on the standard "Visual Composer" tab structure found in S3WaaS sites. If a site uses a custom layout or heavily customized theme that deviates from the `vc_tta-tabs` structure, scraping might fail for that specific site.
> **Deep Scraping**: Visiting every notice link increases traffic significantly. We will add a small delay to be polite.

## Proposed Changes

### Scraping Logic ([s3waas_scraper.py](file:///e:/darshi/s3waas-elements-scraper/s3waas_scraper.py))
1.  **Target Categories**:
    -   "Notice" / "Notices"
    -   "Tender" / "Tenders"
    -   "Recruitment" / "Recruitments"
    -   "What's New" / "Latest Updates"
    -   "Press Release" / "Press Releases"

2.  **Algorithm**:
    -   **Step 1**: Load Homepage HTML.
    -   **Step 2**: Find all tab anchors & extract content IDs.
    -   **Step 3**: Extract list items (Text + Link) from these containers.
    -   **Step 4 (Deep Resolve)**: For each extracted link:
        -   If the link ends in `.pdf`, `.doc`, etc., keep it as is.
        -   If the link is a webpage (local domain):
            -   **Fetch** the intermediate page.
            -   **Search** for the first/most relevant document link inside it (looking for `.pdf` extensions or "View"/"Download" text).
            -   **Add** this resolved link as `pdf_url` to the data item.

3.  **Output Structure ([scraped_content.json](file:///e:/darshi/s3waas-elements-scraper/scraped_content.json))**:
    ```json
    {
      "District Name": {
        "url": "...",
        "data": {
          "Notices": [
            { 
              "text": "District Environment Plan", 
              "url": "https://district.gov.in/notice/environment-plan", 
              "pdf_url": "https://cdn.s3waas.gov.in/s3.../uploads/...pdf" 
            }
          ]
        }
      }
    }
    ```

## Files
### [MODIFY] [s3waas_scraper.py](file:///e:/darshi/s3waas-elements-scraper/s3waas_scraper.py)
-   Add `resolve_pdf_link(session, url)` function.
-   Integrate this resolution step into the main extraction loop.

## Verification Plan
1.  **Dry Run**: Run on `https://ranchi.nic.in` (known to have intermediate "View" pages).
2.  **Inspect Output**: Check [scraped_content.json](file:///e:/darshi/s3waas-elements-scraper/scraped_content.json) for populated `pdf_url` fields.
3.  **Full Run**: Execute on the full list.
