import React, { useEffect, useState, useContext } from "react";
import { Row, Container, Form, Button, Col } from "@themesberg/react-bootstrap";
import Chart from "./components/Chart";
import { TabTitle } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";
import { useHistory, useLocation } from "react-router";


export default () => {
  TabTitle("Data Analytics");

  const history = useHistory();
  const location = useLocation();
  const itemType = location.pathname.split("/").slice(-1)[0];
  const {fetchRequest} = useContext(AppContext);
  const [filters, setFilters] = useState({});
  const [queries, setQueries] = useState({});
  const [charts, setCharts] = useState([]);


  const getReports = () => {
    fetchRequest(`data/get-reports-analytics/${itemType}`, 'POST',
    JSON.stringify(queries), false)
    .then((data) => {
      if (data != undefined) {
        setFilters(data.filters);
        setCharts(data.charts);
      }
    }).catch((err) => alert(err));
  }

  useEffect(() => {
    getReports();
  }, [itemType]);

  const handleSubmitForm = (e) => {
    e.preventDefault();
    getReports();
  }

  const handleSelectQuery = (value, id) => {
    var newQueries = queries;
    newQueries[id] = value;
    console.log(newQueries);
    setQueries({...newQueries});
  }

  return (
    <article>
      <Container>
        <Row>
        <Col>
          <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-4">
            <Form className='row' onSubmit={(e) => handleSubmitForm(e)}>
              {
                Object.keys(filters).map((key, index) => {
                  var filter = filters[key];
                  if (filter.type == 'date') {
                    return (
                      <Form.Group className="mb-3 col-12" key={index}>
                        <Form.Label>{filter.label}</Form.Label>
                        <Form.Control
                          type="date"
                          value={queries[filter.id] ? queries[filter.id] : filter.value}
                          onChange={(e) => {handleSelectQuery(e.target.value, filter.id)}}
                        />
                      </Form.Group>
                    )
                  } else if (filter.type == 'select') {
                    return (
                      <Form.Group className="mb-3 col-12" key={index}>
                        <Form.Label>{filter.label}</Form.Label>
                        <Form.Control
                          as="select"
                          value={queries[filter.id] ? queries[filter.id] : filter.value}
                          onChange={(e) => {handleSelectQuery(e.target.value, filter.id)}}
                        >
                          { 'isAll' in filter && !filter.isAll ? 
                            <></> : <option value={'All'} key={0}>
                              All
                            </option>
                          }
                          {filter.options.map((item, idx) => (
                            <option value={item} key={idx+1}>
                              {item}
                            </option>
                          ))}
                        </Form.Control>
                      </Form.Group>
                    )
                  }
                })
              }
              <Row className="d-flex justify-content-center flex-nowrap">
                <Button
                  variant="primary"
                  className="m-1 mb-3"
                  type="submit"
                  style={{ width: 200 }}
                >
                  Search
                </Button>
              </Row>
            </Form>
          </Row>
        </Col>
        <Col xs={9}>
          <Row className="mt-3">
            {charts.map((chart, index) => (
              <Chart key={chart.random} rawChart={chart} />
            ))}
          </Row>
        </Col>
        </Row>
      </Container>
    </article>
  );
};
