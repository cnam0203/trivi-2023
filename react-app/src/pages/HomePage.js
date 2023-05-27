import React, { useState, useEffect } from "react";
import { Route, Switch, Redirect } from "react-router-dom";
import { Routes } from "../routes";

// pages
import Form from "./Form";
import Signin from "./Signin";
import Signup from "./Signup";
import ImportAPI from "./ImportAPI";
import ImportFile from "./ImportFile";
import ListItems from "./ListItems";
import DeleteItems from "./DeleteItems";
import Configuration from "./Configuration";
import Documentation from "./Documentation";
import Analytics from "./Analytics";
import Recommend from "./Recommend";
import NotFoundPage from "./examples/NotFound";
import ServerError from "./examples/ServerError";
import DashboardOverview from "./DashboardOverview";
import ForgotPassword from "./ForgotPassword";
import ImportHistory from "./ImportHistory";
import MatchingTemplate from './MatchingTemplate';
import NewTemplate from './NewTemplate';
import DetailTemplate from './DetailTemplate';
import ListModels from './ListModels';
import ModelDetail from './ModelDetail';
import NewModel from './NewModel';
import TestAPI from './TestAPI';

// components
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import Preloader from "../components/Preloader";

import Upgrade from "./Upgrade";
import Transactions from "./Transactions";
import Settings from "./Settings";
import BootstrapTables from "./tables/BootstrapTables";
import ResetPassword from "./examples/ResetPassword";
import Lock from "./examples/Lock";
import Profile from "./Profile";
import Organization from "./Organization";

// documentation pages
import DocsOverview from "./documentation/DocsOverview";
import DocsDownload from "./documentation/DocsDownload";
import DocsQuickStart from "./documentation/DocsQuickStart";
import DocsLicense from "./documentation/DocsLicense";
import DocsFolderStructure from "./documentation/DocsFolderStructure";
import DocsBuild from "./documentation/DocsBuild";
import DocsChangelog from "./documentation/DocsChangelog";
import Accordion from "./components/Accordion";
import Alerts from "./components/Alerts";
import Badges from "./components/Badges";
import Breadcrumbs from "./components/Breadcrumbs";
import Buttons from "./components/Buttons";
import Forms from "./components/Forms";
import Modals from "./components/Modals";
import Navs from "./components/Navs";
import Navbars from "./components/Navbars";
import Pagination from "./components/Pagination";
import Popovers from "./components/Popovers";
import Progress from "./components/Progress";
import Tables from "./components/Tables";
import Tabs from "./components/Tabs";
import Tooltips from "./components/Tooltips";
import Toasts from "./components/Toasts";

const RouteWithLoader = ({ component: Component, ...rest }) => {
  const [loaded, setLoaded] = useState(false);
  const login = localStorage.getItem('token') ? true : false;

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Route
      {...rest}
      render={(props) =>
        login && rest.path === Routes.Signin.path ? (
          <Redirect to={Routes.DashboardOverview.path} />
        ) : (
          <>
            {" "}
            <Preloader show={loaded ? false : true} /> <Component {...props} />{" "}
          </>
        )
      }
    />
  );
};

const RouteWithSidebar = ({ component: Component, ...rest }) => {
  const [loaded, setLoaded] = useState(false);
  const login = localStorage.getItem('token') ? true : false;

  useEffect(() => {
    const timer = setTimeout(() => setLoaded(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  const localStorageIsSettingsVisible = () => {
    return localStorage.getItem("settingsVisible") === "false" ? false : true;
  };

  const [showSettings, setShowSettings] = useState(
    localStorageIsSettingsVisible
  );

  const toggleSettings = () => {
    setShowSettings(!showSettings);
    localStorage.setItem("settingsVisible", !showSettings);
  };

  return (
    <Route
      {...rest}
      render={(props) =>
        login ? (
          <>
            <Preloader show={loaded ? false : true} />
            <Sidebar />

            <main className="content">
              <Navbar />
              <Component {...props} />
              <Footer
                toggleSettings={toggleSettings}
                showSettings={showSettings}
              />
            </main>
          </>
        ) : (
          <Redirect to={Routes.Signin.path} />
        )
      }
    />
  );
};

export default () => (
  <Switch>
    <RouteWithLoader exact path={Routes.Signin.path} component={Signin} />
    <RouteWithLoader exact path={Routes.Signup.path} component={Signup} />
    <RouteWithLoader
      exact
      path={Routes.NotFound.path}
      component={NotFoundPage}
    />
    <RouteWithLoader
      exact
      path={Routes.ServerError.path}
      component={ServerError}
    />
    <RouteWithSidebar
      exact
      path={Routes.Presentation.path}
      component={DashboardOverview}
    />
    <RouteWithSidebar
      exact
      path={Routes.DashboardOverview.path}
      component={DashboardOverview}
    />
    <RouteWithSidebar
      path={Routes.ListItems.path}
      component={ListItems}
    />
    <RouteWithSidebar
      path={Routes.Analytics.path}
      component={Analytics}
    />
    <RouteWithSidebar
      path={Routes.MatchingTemplate.path}
      component={MatchingTemplate}
    />
    <RouteWithSidebar
      path={Routes.NewTemplate.path}
      component={NewTemplate}
    />
    <RouteWithSidebar
      path={Routes.DetailTemplate.path}
      component={DetailTemplate}
    />
    <RouteWithSidebar path={Routes.ItemDetail.path} component={Form} />
    <RouteWithSidebar path={Routes.ImportAPI.path} component={ImportAPI} />
    <RouteWithSidebar path={Routes.ImportFile.path} component={ImportFile} />
    <RouteWithSidebar path={Routes.ImportHistory.path} component={ImportHistory} />
    <RouteWithSidebar path={Routes.DeleteItems.path} component={DeleteItems} />
    <RouteWithSidebar
      path={Routes.ListModels.path}
      component={ListModels}
    />
    <RouteWithSidebar
      path={Routes.ModelDetail.path}
      component={ModelDetail}
    />
    <RouteWithSidebar
      path={Routes.ModelRun.path}
      component={NewModel}
    />
    <RouteWithSidebar
      path={Routes.TestAPI.path}
      component={TestAPI}
    />
    <RouteWithSidebar
      exact
      path={Routes.Recommend.path}
      component={Recommend}
    />
    <RouteWithSidebar
      exact
      path={Routes.Configuration.path}
      component={Configuration}
    />
    <RouteWithSidebar
      exact
      path={Routes.Analytics2.path}
      component={Analytics}
    />
    <RouteWithSidebar
      exact
      path={Routes.Documentation.path}
      component={Documentation}
    />
    <RouteWithLoader
      exact
      path={Routes.ForgotPassword.path}
      component={ForgotPassword}
    />
    <RouteWithSidebar exact path={Routes.Profile.path} component={Profile} />
    <RouteWithSidebar exact path={Routes.Organization.path} component={Organization} />
    <Redirect to={Routes.NotFound.path} />
    {/* <RouteWithSidebar exact path={Routes.Profile.path} component={Profile} />
    <RouteWithLoader exact path={Routes.Signup.path} component={Signup} />
    <RouteWithLoader
      exact
      path={Routes.ForgotPassword.path}
      component={ForgotPassword}
    />
    <RouteWithLoader
      exact
      path={Routes.ResetPassword.path}
      component={ResetPassword}
    />
    <RouteWithLoader exact path={Routes.Lock.path} component={Lock} />
    
    <RouteWithSidebar exact path={Routes.Upgrade.path} component={Upgrade} />
    <RouteWithSidebar
      exact
      path={Routes.Transactions.path}
      component={Transactions}
    />
    <RouteWithSidebar exact path={Routes.Settings.path} component={Settings} />
    <RouteWithSidebar
      exact
      path={Routes.BootstrapTables.path}
      component={BootstrapTables}
    /> */}
    {/* components */}
    {/* <RouteWithSidebar
      exact
      path={Routes.Accordions.path}
      component={Accordion}
    />
    <RouteWithSidebar exact path={Routes.Alerts.path} component={Alerts} />
    <RouteWithSidebar exact path={Routes.Badges.path} component={Badges} />
    <RouteWithSidebar
      exact
      path={Routes.Breadcrumbs.path}
      component={Breadcrumbs}
    />
    <RouteWithSidebar exact path={Routes.Buttons.path} component={Buttons} />
    <RouteWithSidebar exact path={Routes.Forms.path} component={Forms} />
    <RouteWithSidebar exact path={Routes.Modals.path} component={Modals} />
    <RouteWithSidebar exact path={Routes.Navs.path} component={Navs} />
    <RouteWithSidebar exact path={Routes.Navbars.path} component={Navbars} />
    <RouteWithSidebar
      exact
      path={Routes.Pagination.path}
      component={Pagination}
    />
    <RouteWithSidebar exact path={Routes.Popovers.path} component={Popovers} />
    <RouteWithSidebar exact path={Routes.Progress.path} component={Progress} />
    <RouteWithSidebar exact path={Routes.Tables.path} component={Tables} />
    <RouteWithSidebar exact path={Routes.Tabs.path} component={Tabs} />
    <RouteWithSidebar exact path={Routes.Tooltips.path} component={Tooltips} />
    <RouteWithSidebar exact path={Routes.Toasts.path} component={Toasts} /> */}

    {/* documentation */}
    {/* <RouteWithSidebar
      exact
      path={Routes.DocsOverview.path}
      component={DocsOverview}
    />
    <RouteWithSidebar
      exact
      path={Routes.DocsDownload.path}
      component={DocsDownload}
    />
    <RouteWithSidebar
      exact
      path={Routes.DocsQuickStart.path}
      component={DocsQuickStart}
    />
    <RouteWithSidebar
      exact
      path={Routes.DocsLicense.path}
      component={DocsLicense}
    />
    <RouteWithSidebar
      exact
      path={Routes.DocsFolderStructure.path}
      component={DocsFolderStructure}
    />
    <RouteWithSidebar
      exact
      path={Routes.DocsBuild.path}
      component={DocsBuild}
    />
    <RouteWithSidebar
      exact
      path={Routes.DocsChangelog.path}
      component={DocsChangelog}
    /> */}
  </Switch>
);
