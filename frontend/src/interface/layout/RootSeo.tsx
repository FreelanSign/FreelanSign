import { Helmet } from 'react-helmet-async';
import { SITE } from '../../lib/constants/site.config';

export default function RootSeo() {
  return (
    <Helmet>
      <title>{SITE.name}</title>
      <meta name="description" content={SITE.description} />
      <link
        rel="icon"
        type="image/png"
        sizes="32x32"
        href="/img/favicon-32.png"
      />
      <link
        rel="icon"
        type="image/png"
        sizes="16x16"
        href="/img/favicon-16.png"
      />
      <link rel="apple-touch-icon" href="/img/apple-touch-icon.png" />

      {/* Open Graph */}
      <meta property="og:site_name" content={SITE.name} />
      <meta property="og:title" content={SITE.name} />
      <meta property="og:description" content={SITE.description} />
      <meta property="og:type" content="website" />
      <meta property="og:url" content={SITE.url} />
      <meta property="og:image" content={`${SITE.url}/img/og-cover.png`} />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={SITE.name} />
      <meta name="twitter:description" content={SITE.description} />
      <meta name="twitter:image" content={`${SITE.url}/img/og-cover.png`} />
    </Helmet>
  );
}
