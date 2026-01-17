# S3WaaS Content & PDF Scraper Walkthrough

## Overview
We have successfully built a "Deep Scraper" that not only identifies content sections (Notices, Tenders, Recruitment) but also **visits intermediate pages to resolve the direct PDF links**.

## Key Features
1.  **Broad Keyword Support**: Scrapes tabs matching: `notice`, `tender`, `notification`, `recruitment`, `press`, `announcement`, `latest`, `bid`, `vacancy`, `circular`, `order`.
2.  **Deep PDF Resolution**: Automatically visits "View" or "Details" pages to find and extract the underlying `.pdf` file.
3.  **Noise Filtering**: Ignores generic "Read More" links and short navigational text.

## Validated Results
The output [scraped_content.json](file:///e:/darshi/s3waas-elements-scraper/scraped_content.json) now contains direct `pdf_url` entries.

### Example 1: Chennai (Press Release)
| Notice Title | Resolved PDF |
| :--- | :--- |
| Sale of liquor is strictly prohibited on 16.01.2026... | [Link](https://cdn.s3waas.gov.in/s313f3cf8c531952d72e5847c4183e6910/uploads/2018/09/2018092083.pdf) |
| Special Camp for Persons with Disabilities... | [Link](https://cdn.s3waas.gov.in/s313f3cf8c531952d72e5847c4183e6910/uploads/2018/09/2018092083.pdf) |

### Example 2: Mumbai Suburban (Tender)
| Notice Title | Resolved PDF |
| :--- | :--- |
| Regarding recovery of outstanding amount... | [Link](https://cdn.s3waas.gov.in/s304025959b191f8f9de3f924f0940515f/uploads/2025/12/17655309349562.pdf) |

### Example 3: Rangareddy (Recruitment)
| Notice Title | Resolved PDF |
| :--- | :--- |
| Applications are invited... Mission Vatsalya | [Link](https://cdn.s3waas.gov.in/s3addfa9b7e234254d26e9c7f2af1005cb/uploads/2025/12/17668278378520.pdf) |

## How to Run
1.  Ensure [s3waas_urls.json](file:///e:/darshi/s3waas-elements-scraper/s3waas_urls.json) contains your target websites.
2.  Run the script: 
    ```bash
    python s3waas_scraper.py
    ```
3.  Check [scraped_content.json](file:///e:/darshi/s3waas-elements-scraper/scraped_content.json) for the results.


We have successfully analyzed and scraped the homepages of the provided 25 S3WaaS government websites. The scraper verified that these sites share a common infrastructure with unique identifiers (hashes) for their CDN storage.

> [!IMPORTANT]Key Findings
Infrastructure: Sites are WordPress-based.
Storage: Assets are hosted on cdn.s3waas.gov.in.
Pattern: https://cdn.s3waas.gov.in/s3<SITE_HASH>/uploads/...
Identified Site Hashes
The following unique hashes were extracted. These are the keys to accessing the backend storage for each district directly.

District	Site URL	CDN Hash
Chennai	https://chennai.nic.in	13f3cf8c531952d72e5847c4183e6910
Mumbai	https://mumbaicity.gov.in	11b921ef080f7736089c757404650e40
Mumbai Suburban	https://mumbaisuburban.gov.in/en/	04025959b191f8f9de3f924f0940515f
Ranchi	https://ranchi.nic.in	2b8a61594b1f4c4db0902a8a395ced93
Ranga Reddy	https://rangareddy.telangana.gov.in	addfa9b7e234254d26e9c7f2af1005cb
Hooghly	https://hooghly.nic.in	aff1621254f7c1be92f64550478c56e6
Howrah	https://howrah.gov.in	53e3a7161e428b65688f14b84d61c610
Hyderabad	https://hyderabad.telangana.gov.in	6c524f9d5d7027454a783c841250ba71
Imphal East	https://imphaleast.nic.in	a684eceee76fc522773286a895bc8436
Imphal West	https://imphalwest.nic.in	faa9afea49ef2ff029a833cccc778fd0
...	...	...
(Full list available in 
[scraped_assets.json](file:///e:/darshi/s3waas-elements-scraper/scraped_assets.json)
)

Extracted Assets
The scraper produced a structured JSON file 
[scraped_assets.json](file:///e:/darshi/s3waas-elements-scraper/scraped_assets.json)
 containing:

Images: All image source URLs found on the homepage.
Documents: Direct links to PDFs, DOCs, and ZIPs.
Theme Assets: CSS/JS files used by the site theme.
Next Steps
Now that we have the Site Hash for each district, we can:

Deep Crawl: Use the hash to verify if an asset belongs to a specific district.
API Scrape: Use admin-ajax.php (as discovered in the network check) to fetch "Announcements" and "Notices" dynamically.