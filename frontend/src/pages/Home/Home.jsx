import React from 'react';
import InstancesTable from "./components/intances-table";
import CurrentTrendsTable from "./components/current-trends-table";
import SuspiciousTrendsTable from "./components/suspicious-trends-table";
import SuspiciousAccountsTable from "./components/suspicious-accounts-table";

const Home = () => {
    return (
        <div>
            <h1>Mastodon Fediverse Suspicious Trends and Accounts Analyser</h1>
            <div>
                <h2><a href="https://github.com/zytfo/mastodon_trend_analyzer">Github Repository</a></h2>
                <h2>Authors: <a href="https://github.com/zytfo/">Artur Khaialiev</a>, <a
                    href="https://ufind.univie.ac.at/de/person.html?id=19954">Paul Fuxjäger</a></h2>
                <h2><a href="http://fediscience.cosy.univie.ac.at/docs/swagger">Swagger Documentation</a></h2>
            </div>
            <br/>
            <br/>
            <div>
                <h1>Tracked Mastodon Instances with Suspicious Entities</h1>
                <InstancesTable/>
            </div>
            <br/>
            <br/>
            <div>
                <h1>Current Mastodon Fediverse Trends</h1>
                <CurrentTrendsTable/>
            </div>
            <br/>
            <br/>
            <div>
                <h1>Suspicious Mastodon Fediverse Trends</h1>
                <SuspiciousTrendsTable/>
            </div>
            <br/>
            <br/>
            <div>
                <h1>Suspicious Mastodon Fediverse Accounts</h1>
                <SuspiciousAccountsTable/>
            </div>
        </div>
    );
};

export default Home;
