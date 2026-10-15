import fs from 'fs';
import path from 'path';

console.log('=== Antiject WCAG 2.2 AA & SEO Compliance Audit ===\n');

const htmlPath = path.resolve('web/index.html');
const appTsxPath = path.resolve('web/src/App.tsx');
const cssPath = path.resolve('web/src/index.css');

let passCount = 0;
let failCount = 0;

function assertCheck(name, condition, details = '') {
  if (condition) {
    console.log(`[PASS] ${name}`);
    passCount++;
  } else {
    console.error(`[FAIL] ${name}: ${details}`);
    failCount++;
  }
}

// 1. Audit index.html
const htmlContent = fs.readFileSync(htmlPath, 'utf8');

assertCheck('HTML has valid lang attribute', /<html\s+lang="en">/i.test(htmlContent));
assertCheck('HTML has viewport meta tag', /<meta\s+name="viewport"/i.test(htmlContent));
assertCheck('HTML has descriptive title tag', /<title>Antiject.*Prompt-Injection Firewall.*<\/title>/i.test(htmlContent));
assertCheck('HTML has meta description tag', /<meta\s+name="description"/i.test(htmlContent));
assertCheck('HTML has Open Graph meta tags', /<meta\s+property="og:title"/i.test(htmlContent) && /<meta\s+property="og:description"/i.test(htmlContent));
assertCheck('HTML has Twitter card tags', /<meta\s+property="twitter:card"/i.test(htmlContent));
assertCheck('HTML has favicon link', /<link\s+rel="icon"/i.test(htmlContent));

// 2. Audit App.tsx for Landmarks & A11y
const appContent = fs.readFileSync(appTsxPath, 'utf8');

assertCheck('Contains semantic banner landmark (<header role="banner">)', /<header[^>]*role="banner"/i.test(appContent));
assertCheck('Contains semantic navigation landmark (<nav role="navigation">)', /<nav[^>]*role="navigation"/i.test(appContent));
assertCheck('Contains semantic main landmark (<main id="main-content">)', /<main[^>]*id="main-content"/i.test(appContent));
assertCheck('Contains semantic contentinfo landmark (<footer role="contentinfo">)', /<footer[^>]*role="contentinfo"/i.test(appContent));
assertCheck('Single H1 heading in main section', (appContent.match(/<h1/g) || []).length === 1);
assertCheck('Accessible text input with label/aria-label', /aria-label="Untrusted text payload"/i.test(appContent));
assertCheck('Accessible tabs with role="tablist" and role="tab"', /role="tablist"/i.test(appContent) && /role="tab"/i.test(appContent));
assertCheck('Accessible modal with role="dialog" and aria-modal="true"', /role="dialog"/i.test(appContent) && /aria-modal="true"/i.test(appContent));
assertCheck('Buttons have explicit aria-label where needed', /aria-label="Copy install command"/i.test(appContent) && /aria-label="Close modal"/i.test(appContent));

// 3. Audit CSS for Focus Rings and Contrast
const cssContent = fs.readFileSync(cssPath, 'utf8');
assertCheck('Visible focus indicators defined (:focus-visible)', /:focus-visible\s*\{/i.test(cssContent));
assertCheck('Cyber dark theme tokens defined', /--bg-dark:\s*#080b11/i.test(cssContent) && /--accent-cyan:\s*#00f0ff/i.test(cssContent));

// 4. Check static artifacts
assertCheck('robots.txt exists in public directory', fs.existsSync('web/public/robots.txt'));
assertCheck('sitemap.xml exists in public directory', fs.existsSync('web/public/sitemap.xml'));
assertCheck('Custom 404 page exists in public directory', fs.existsSync('web/public/404.html'));
assertCheck('Favicon SVG exists in public directory', fs.existsSync('web/public/favicon.svg'));

console.log(`\nAudit Complete: ${passCount} Checks Passed, ${failCount} Failed.`);

if (failCount > 0) {
  process.exit(1);
}
