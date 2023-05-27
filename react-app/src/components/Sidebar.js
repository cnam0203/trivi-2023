import React, { useState } from "react";
import SimpleBar from "simplebar-react";
import { useLocation, useHistory } from "react-router-dom";
import { CSSTransition } from "react-transition-group";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faBook,
  faChartPie,
  faSignOutAlt,
  faTimes,
  faShareAlt,
  faChartBar,
  faFileAlt,
  faUser
} from "@fortawesome/free-solid-svg-icons";
import {
  Nav,
  Badge,
  Image,
  Button,
  Accordion,
  Navbar,
} from "@themesberg/react-bootstrap";
import { Link } from "react-router-dom";

import { Routes } from "../routes";
import ReactHero from "../assets/img/technologies/react-hero-logo.svg";
import Logo from "../assets/img/technologies/logo.svg";

export default (props = {}) => {
  const location = useLocation();
  const history = useHistory();
  const [show, setShow] = useState(false);
  const { pathname } = location;
  const showClass = show ? "show" : "";

  const onCollapse = () => setShow(!show);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    history.push("/sign-in");
  };

  const CollapsableNavItem = (props) => {
    const { eventKey, title, icon, children = null } = props;
    const defaultKey = pathname.indexOf(eventKey) !== -1 ? eventKey : "";

    return (
      <Accordion as={Nav.Item} defaultActiveKey={defaultKey} className="">
        <Accordion.Item eventKey={eventKey}>
          <Accordion.Button
            as={Nav.Link}
            className="d-flex justify-content-between align-items-center"
          >
            <span>
              <span className="sidebar-icon">
                <FontAwesomeIcon icon={icon} />{" "}
              </span>
              <span className="sidebar-text">{title}</span>
            </span>
          </Accordion.Button>
          <Accordion.Body className="multi-level">
            <Nav className="flex-column">{children}</Nav>
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    );
  };

  const NavItem = (props) => {
    const {
      title,
      link,
      external,
      target,
      icon,
      image,
      badgeText,
      badgeBg = "secondary",
      badgeColor = "primary",
    } = props;
    const classNames = badgeText
      ? "d-flex justify-content-start align-items-center justify-content-between"
      : "";
    const navItemClassName = link === pathname ? "active" : "";
    const linkProps = external ? { href: link } : { as: Link, to: link };

    return (
      <Nav.Item
        className={navItemClassName}
        style={{ marginBottom: image ? "2.5rem" : "0" }}
        onClick={() => setShow(false)}
      >
        <Nav.Link {...linkProps} target={target} className={classNames}>
          <span>
            {icon ? (
              <span className="sidebar-icon">
                <FontAwesomeIcon icon={icon} />{" "}
              </span>
            ) : null}
            {image ? (
              <Image
                src={image}
                width={40}
                height={40}
                className="sidebar-icon svg-icon"
              />
            ) : null}

            <span
              className="sidebar-text"
              style={{ fontSize: image ? "1.5rem" : "1rem" }}
            >
              {title}
            </span>
          </span>
          {badgeText ? (
            <Badge
              pill
              bg={badgeBg}
              text={badgeColor}
              className="badge-md notification-count ms-2"
            >
              {badgeText}
            </Badge>
          ) : null}
        </Nav.Link>
      </Nav.Item>
    );
  };

  return (
    <>
      <Navbar
        expand={false}
        collapseOnSelect
        variant="dark"
        className="navbar-theme-primary px-4 d-md-none"
      >
        <Navbar.Brand
          className="me-lg-5"
          as={Link}
          to={Routes.DashboardOverview.path}
        >
          <Image src={ReactHero} className="navbar-brand-light" />
        </Navbar.Brand>
        <Navbar.Toggle
          as={Button}
          aria-controls="main-navbar"
          onClick={onCollapse}
        >
          <span className="navbar-toggler-icon" />
        </Navbar.Toggle>
      </Navbar>
      <CSSTransition timeout={300} in={show} classNames="sidebar-transition">
        <SimpleBar
          className={`collapse ${showClass} sidebar d-md-block bg-primary text-white`}
        >
          <div className="sidebar-inner px-1 pt-3">
            <div className="user-card d-flex d-md-none align-items-center justify-content-between justify-content-md-center pb-4">
              <Nav.Link
                className="collapse-close d-md-none"
                onClick={onCollapse}
              >
                <FontAwesomeIcon icon={faTimes} />
              </Nav.Link>
            </div>
            <Nav className="flex-column pt-3 pt-md-0">
              <NavItem
                title="RecomSys"
                link={Routes.Presentation.path}
                image={Logo}
              />
              <NavItem
                title="Dashboard"
                link={Routes.DashboardOverview.path}
                icon={faChartPie}
              />
              <CollapsableNavItem
                eventKey={Routes.ListItems.path}
                title="Data Management"
                icon={faFileAlt}
              >
                <NavItem title="Customer Profile" link={Routes.ListItems.path + Routes.Customer.path} />
                <NavItem title="Product" link={Routes.ListItems.path + Routes.Product.path}/>
                <NavItem title="Item" link={Routes.ListItems.path + Routes.Item.path}/>
                <NavItem title="Event" link={Routes.ListItems.path + Routes.Event.path} />
                <NavItem title="Transaction" link={Routes.ListItems.path + Routes.Transaction.path}/>
                <NavItem title="Event-Item" link={Routes.ListItems.path + Routes.EventItem.path} />
                <NavItem title="Transaction-Item" link={Routes.ListItems.path + Routes.TransactionItem.path}/>
              </CollapsableNavItem>
              <CollapsableNavItem
                eventKey={Routes.Analytics.path}
                title="Data Reports"
                icon={faChartBar}
              >
                <NavItem title="Customer" link={Routes.Analytics.path + Routes.Customer.path} />
                <NavItem title="Event - Behavior" link={Routes.Analytics.path + Routes.Event.path} />
                <NavItem title="Product" link={Routes.Analytics.path + Routes.Item.path}/>
                <NavItem title="Transaction" link={Routes.Analytics.path + Routes.Transaction.path}/>
              </CollapsableNavItem>
              <CollapsableNavItem
                eventKey={Routes.ListModels.path}
                title="Data Analytics"
                icon={faShareAlt}
              >
                <NavItem title="Customer Segmentation" link={Routes.ListModels.path + Routes.CustomerSegmentation.path} />
                <NavItem title="Product Recommendation" link={Routes.ListModels.path + Routes.ProductRecommendation.path} />
                <NavItem title="Association Rule" link={Routes.ListModels.path + Routes.AssociationRule.path} />
                <NavItem title="Correlation" link={Routes.ListModels.path + Routes.Correlation.path} />
              </CollapsableNavItem>
              {/* <CollapsableNavItem
                eventKey="recommend/"
                title="Recommendation"
                icon={faShareAlt}
              >
                <NavItem
                  title="Configuration"
                  link={Routes.Configuration.path}
                />
                <NavItem
                  title="API Integration"
                  link={Routes.Recommend.path}
                />
              </CollapsableNavItem> */}
              <NavItem
                title="Documentation"
                icon={faBook}
                link={Routes.Documentation.path}
              />

              {/* <CollapsableNavItem eventKey="tables/" title="Tables" icon={faTable}>
                <NavItem title="Bootstrap Table" link={Routes.BootstrapTables.path} />
              </CollapsableNavItem> */}

              {/* <CollapsableNavItem eventKey="examples/" title="Page Examples" icon={faFileAlt}>
                <NavItem title="Sign In" link={Routes.Signin.path} />
                <NavItem title="Sign Up" link={Routes.Signup.path} />
                <NavItem title="Forgot password" link={Routes.ForgotPassword.path} />
                <NavItem title="Reset password" link={Routes.ResetPassword.path} />
                <NavItem title="Lock" link={Routes.Lock.path} />
                <NavItem title="404 Not Found" link={Routes.NotFound.path} />
                <NavItem title="500 Server Error" link={Routes.ServerError.path} />
              </CollapsableNavItem> */}

              {/* <NavItem external title="Plugins" link="https://demo.themesberg.com/volt-pro-react/#/plugins/datatable" target="_blank" badgeText="Pro" icon={faChartPie} /> */}

              {/* <Dropdown.Divider className="my-3 border-indigo" /> */}

              {/* <CollapsableNavItem eventKey="documentation/" title="Getting Started" icon={faBook}>
                <NavItem title="Overview" link={Routes.DocsOverview.path} />
                <NavItem title="Download" link={Routes.DocsDownload.path} />
                <NavItem title="Quick Start" link={Routes.DocsQuickStart.path} />
                <NavItem title="License" link={Routes.DocsLicense.path} />
                <NavItem title="Folder Structure" link={Routes.DocsFolderStructure.path} />
                <NavItem title="Build Tools" link={Routes.DocsBuild.path} />
                <NavItem title="Changelog" link={Routes.DocsChangelog.path} />
              </CollapsableNavItem> */}
              {/* <CollapsableNavItem eventKey="components/" title="Components" icon={faBoxOpen}>
                <NavItem title="Accordion" link={Routes.Accordions.path} />
                <NavItem title="Alerts" link={Routes.Alerts.path} />
                <NavItem title="Badges" link={Routes.Badges.path} />
                <NavItem external title="Widgets" link="https://demo.themesberg.com/volt-pro-react/#/components/widgets" target="_blank" badgeText="Pro" />
                <NavItem title="Breadcrumbs" link={Routes.Breadcrumbs.path} />
                <NavItem title="Buttons" link={Routes.Buttons.path} />
                <NavItem title="Forms" link={Routes.Forms.path} />
                <NavItem title="Modals" link={Routes.Modals.path} />
                <NavItem title="Navbars" link={Routes.Navbars.path} />
                <NavItem title="Navs" link={Routes.Navs.path} />
                <NavItem title="Pagination" link={Routes.Pagination.path} />
                <NavItem title="Popovers" link={Routes.Popovers.path} />
                <NavItem title="Progress" link={Routes.Progress.path} />
                <NavItem title="Tables" link={Routes.Tables.path} />
                <NavItem title="Tabs" link={Routes.Tabs.path} />
                <NavItem title="Toasts" link={Routes.Toasts.path} />
                <NavItem title="Tooltips" link={Routes.Tooltips.path} />
              </CollapsableNavItem> */}
              {/* <NavItem external title="Themesberg" link="https://themesberg.com" target="_blank" image={ThemesbergLogo} /> */}
              <Button
                variant="secondary"
                className="upgrade-to-pro"
                onClick={handleLogout}
              >
                <FontAwesomeIcon icon={faSignOutAlt} className="me-1" />
                Log out
              </Button>
            </Nav>
          </div>
        </SimpleBar>
      </CSSTransition>
    </>
  );
};
