import type {ReactNode} from 'react';
import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageHero from '@site/src/components/HomepageHero';
import HomepageSections from '@site/src/components/HomepageSections';

import styles from './index.module.css';

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Physical AI & Humanoid Robotics - Embodied Intelligence in the Physical World">
      <main>
        <HomepageHero
          title={siteConfig.title}
          subtitle={siteConfig.tagline}
          ctaText="Start Learning"
          ctaUrl="/docs/intro"
        />
        <HomepageSections />
      </main>
    </Layout>
  );
}
