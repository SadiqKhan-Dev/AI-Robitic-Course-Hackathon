import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Heading from '@theme/Heading';

import styles from './styles.module.css';

interface HomepageHeroProps {
  title?: string;
  subtitle?: string;
  ctaText?: string;
  ctaUrl?: string;
}

const HomepageHero: React.FC<HomepageHeroProps> = ({
  title,
  subtitle,
  ctaText = 'Get Started',
  ctaUrl = '/docs/intro'
}) => {
  const {siteConfig} = useDocusaurusContext();
  
  // Use defaults if props are not provided
  const heroTitle = title || siteConfig.title || 'Physical AI & Humanoid Robotics';
  const heroSubtitle = subtitle || siteConfig.tagline || 'Embodied Intelligence in the Physical World';

  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className={clsx('hero__title', styles.heroTitle)}>
          {heroTitle}
        </Heading>
        <p className={clsx('hero__subtitle', styles.heroSubtitle)}>
          {heroSubtitle}
        </p>
        <div className={styles.buttons}>
          <Link
            className={clsx('button button--secondary button--lg', styles.heroButton)}
            to={ctaUrl}>
            {ctaText}
          </Link>
        </div>
      </div>
    </header>
  );
};

export default HomepageHero;