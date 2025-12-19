import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

interface ModuleCardProps {
  title: string;
  description: string;
  imageUrl: string;
  linkUrl: string;
  color?: string;
  position?: number;
}

const ModuleCard: React.FC<ModuleCardProps> = ({
  title,
  description,
  imageUrl,
  linkUrl,
  color = 'var(--ifm-color-primary)',
}) => {
  return (
    <div className={clsx('col col--4', styles.moduleCardContainer)}>
      <div 
        className={clsx('card', styles.moduleCard)}
        style={{borderTop: `4px solid ${color}`}}
      >
        <div className={styles.cardImageContainer}>
          {imageUrl ? (
            <img 
              src={imageUrl} 
              alt={title}
              className={styles.cardImage}
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.onerror = null; // Prevent infinite loop if fallback fails
                target.src = '/img/logo.svg'; // Fallback image
              }}
            />
          ) : (
            <div className={styles.placeholderImage} style={{backgroundColor: color}}>
              <span className={styles.placeholderText}>{title.charAt(0)}</span>
            </div>
          )}
        </div>
        
        <div className="card__body">
          <h3 className={styles.cardTitle}>{title}</h3>
          <p className={styles.cardDescription}>{description}</p>
        </div>
        
        <div className="card__footer">
          <Link className={clsx('button button--outline button--primary', styles.cardButton)} to={linkUrl}>
            Explore Module
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ModuleCard;