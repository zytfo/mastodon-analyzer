import React, { useState, useEffect } from 'react';
import { Shield, TrendingUp, Users, FileText, AlertTriangle, Activity } from 'lucide-react';
import axios from 'axios';
import styles from './Home.module.css';
import SuspiciousStatusesTable from './components/suspicious-statuses-table';
import InstancesTable from './components/intances-table';
import CurrentTrendsTable from './components/current-trends-table';
import SuspiciousTrendsTable from './components/suspicious-trends-table';
import SuspiciousAccountsTable from './components/suspicious-accounts-table';

const Home = () => {
    const [activeTab, setActiveTab] = useState('statuses');

    const tabs = [
        { id: 'statuses', label: 'Suspicious Statuses', icon: FileText },
        { id: 'instances', label: 'Instances', icon: Activity },
        { id: 'trends', label: 'Current Trends', icon: TrendingUp },
        { id: 'suspicious-trends', label: 'Suspicious Trends', icon: AlertTriangle },
        { id: 'accounts', label: 'Suspicious Accounts', icon: Users }
    ];

    return (
        <div className={styles.pageWrapper}>
            {/* Header */}
            <header className={styles.header}>
                <div className={styles.headerContent}>
                    <div className={styles.logoSection}>
                        <div className={styles.logoIcon}>
                            <Shield size={32} color="white" />
                        </div>
                        <div className={styles.logoText}>
                            <h1>Mastodon Analyzer</h1>
                            <p>Leveraging LLMs to Identify Disinformation</p>
                        </div>
                    </div>
                    <div className={styles.headerButtons}>
                        <a
                            href="https://fediversechecker.org/docs/swagger"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`${styles.headerButton} ${styles.headerButtonSecondary}`}
                        >
                            API Docs
                        </a>
                        <a
                            href="https://github.com/zytfo/mastodon-analyzer"
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`${styles.headerButton} ${styles.headerButtonPrimary}`}
                        >
                            GitHub
                        </a>
                    </div>
                </div>
            </header>

            <div className={styles.container}>
                {/* Navigation Tabs */}
                <div className={styles.tabsContainer}>
                    <div className={styles.tabs}>
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ''}`}
                            >
                                <tab.icon size={16} />
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content Area */}
                <div className={styles.contentCard}>
                    {activeTab === 'statuses' && (
                        <div>
                            <div className={styles.contentHeader}>
                                <h2 className={styles.contentTitle}>Suspicious Statuses</h2>
                            </div>
                            <SuspiciousStatusesTable />
                        </div>
                    )}

                    {activeTab === 'instances' && (
                        <div>
                            <h2 className={styles.contentTitle} style={{marginBottom: '1.5rem'}}>Tracked Mastodon Instances</h2>
                            <InstancesTable />
                        </div>
                    )}

                    {activeTab === 'trends' && (
                        <div>
                            <h2 className={styles.contentTitle} style={{marginBottom: '1.5rem'}}>Current Mastodon Trends</h2>
                            <CurrentTrendsTable />
                        </div>
                    )}

                    {activeTab === 'suspicious-trends' && (
                        <div>
                            <h2 className={styles.contentTitle} style={{marginBottom: '1.5rem'}}>Suspicious Trends</h2>
                            <SuspiciousTrendsTable />
                        </div>
                    )}

                    {activeTab === 'accounts' && (
                        <div>
                            <h2 className={styles.contentTitle} style={{marginBottom: '1.5rem'}}>Suspicious Accounts</h2>
                            <SuspiciousAccountsTable />
                        </div>
                    )}
                </div>

                {/* Footer Info */}
                <div className={styles.footer}>
                    <p>
                        Authors: {' '}
                        <a href="https://github.com/zytfo/">Artur Khaialiev</a>
                        {', '}
                        <a href="https://ufind.univie.ac.at/de/person.html?id=19954">Paul Fuxjäger</a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Home;