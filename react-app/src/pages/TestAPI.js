import React, { useState, useEffect, useContext, useRef } from "react";
import {
  Col,
  Row,
  Form,
  Container,
  Button,
  Modal,
  Table,
  Card,
  Alert
} from "@themesberg/react-bootstrap";
import { useHistory, useLocation } from "react-router";
import { TabTitle } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";
import ProcessTables from "./tables/ProcessTables";
import { usePapaParse, useCSVReader } from 'react-papaparse';
import { PageCustomizedTable} from "../components/Tables";

export default () => {  
  const refFile = useRef(null);
  const {fetchRequest} = useContext(AppContext);
  const history = useHistory();
  const location = useLocation();
  const [showModal, setShowModal] = useState(false);
  const urlArrays = location.pathname.split("/");
  const itemType = urlArrays[urlArrays.length - 2];
  const itemId = urlArrays[urlArrays.length - 1];
  const [api, setAPI] = useState('');
  const [itemLabel, setItemLabel] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [result, setResult] = useState({});

  const [showAlert, setShowAlert] = useState(false);
  const [successAlert, setSuccessAlert] = useState(true);
  const [alertMsg, setAlertMsg] = useState('');

  TabTitle(`Test API - ${itemType}`);

  useEffect(() => {
    console.log("Hello")
    fetchRequest(`knowledge/get-api-info/${itemType}/${itemId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAPI(data.api)
          setItemLabel(data.item_label)
        }
      }
    }).catch((err) => alert(err));
  }, []);


  const handleOpenModal = (e) => {
    e.preventDefault();
  };

  const handleFormSubmit = (event) => {
    event.preventDefault();
    // Call API to update user object information
    fetchRequest(`knowledge/get-test-model-api/${itemType}/${itemId}/${customerId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setResult(data.result);
          setAlertValue(true, true, 'Get result successfully')
        } else {
          setAlertValue(true, false, data.message)
        }
      }
    }).catch((err) => alert(err));
  }

  const setAlertValue = (isShow, isSuccess, msg) => {
    setShowAlert(isShow);
    setSuccessAlert(isSuccess);
    setAlertMsg(msg);
    setTimeout(() => {
      handleCloseAlert();
    }, 3000)
  }

  const handleCloseAlert = () => {
    setShowAlert(false);
    setSuccessAlert(true);
    setAlertMsg('');
  }

  return (
    <article>
      <Container className="px-0">
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center pt-3">
          <Col className="d-block mb-2 mb-md-0">
            <h1 className="h2">Test API - {itemType}</h1>
          </Col>
        </Row>
        <Alert show={showAlert} variant={successAlert ? 'success' : 'danger'}>
          <Alert.Heading>{alertMsg}</Alert.Heading>
        </Alert>
        <Card className="mb-2">
          <Card.Body>
          <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
            <Form className="row" onSubmit={handleFormSubmit}>
                <Form.Group className="mb-3 col-6">
                    <Form.Label>{`API used for ${itemType}:`}</Form.Label>
                    <Form.Control type="text" value={api} readOnly/>
                </Form.Group>
                <Form.Group className="mb-3 col-6">
                    <Form.Label>{itemLabel}: </Form.Label>
                    <Form.Control type="text" value={customerId} onChange={(event) => setCustomerId(event.target.value)} required/>
                </Form.Group>
                <div className="row"> 
                    <div className="col text-center">
                    <Button variant="primary" type="submit" className="m-1">
                        Get results
                    </Button>
                    </div>
                </div>
            </Form>
          </Row>
          <Row className="d-flex flex-wrap flex-md-nowrap justify-content-center align-items-center py-3">
          {(() => {
              switch(result.type) {
                case 'text':
                  return (
                    <Form className="row">
                        <Form.Group className="mb-3 col-6">
                            <Form.Label>{result.label}: </Form.Label>
                            <Form.Control type="text" value={result.value} readOnly />
                        </Form.Group>
                    </Form>
                  );
                case 'table':
                  return (
                    <PageCustomizedTable info={result.info} width={8} isShowHeader={true}/>
                  );
                default:
                  return <></>;
              }
            })()}
          </Row>
          </Card.Body>
        </Card>
      </Container>
    </article>
  );
};
