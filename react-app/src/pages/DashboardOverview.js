import React, { useEffect, useState, useContext } from "react";
import { faCashRegister, faChartLine } from "@fortawesome/free-solid-svg-icons";
import { Col, Row, Card, Nav, Container, Tab } from "@themesberg/react-bootstrap";
import { faDesktop, faMobileAlt, faTabletAlt } from '@fortawesome/free-solid-svg-icons';


import { CounterWidget, CircleChartWidget } from "../components/Widgets";
import { PageCustomizedTable} from "../components/Tables";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { TabTitle } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";

require("highcharts/modules/exporting")(Highcharts);
require("highcharts/modules/export-data.js")(Highcharts);

export default () => {
  TabTitle("Dashboard");

  const {fetchRequest} = useContext(AppContext);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchRequest("data/get-reports-kpi", 'GET')
    .then((data) => {
      if (data != undefined) {
        setChartData(data.reports)
      }
    }).catch((err) => alert(err));
  }, []);

  return (
    <article>
      <Container className="px-0">
        <Card className="mt-2">
          <Card.Body>
          {chartData.length > 0 && <Tab.Container defaultActiveKey={chartData.length > 0 ? chartData[0].tabName : ''}>
              <Nav fill variant="pills" className="flex-column flex-sm-row">
                {
                  chartData.map((tab, index) => (
                  <Nav.Item key={index} >
                    <Nav.Link eventKey={tab.tabName} className="mb-sm-3 mb-md-0">
                      {tab.tabName}
                    </Nav.Link>
                  </Nav.Item>))
                }
              </Nav>
              <Tab.Content>
                {
                  chartData.map((tab, index) => (
                    <Tab.Pane eventKey={tab.tabName} key={index} className="py-4">
                      <Row>
                      {
                        tab.data.map((report, index) => {
                          if (report.type == 'svg') {
                            return  <CounterWidget info={report} key={index}/>
                          } else if (report.type == 'pie') {
                            return <CircleChartWidget info={report} key={index}/>
                          } else if (report.type == 'table') {
                            return <PageCustomizedTable info={report} key={index}/>
                          }
                        })
                      }
                      </Row>
                    </Tab.Pane>
                  ))
                }
              </Tab.Content>
            </Tab.Container>}
          </Card.Body>
        </Card>
      </Container>
      <>
    </>
    </article>
  );
};
