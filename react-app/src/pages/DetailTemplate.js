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


export default () => {  
  const refFile = useRef(null);
  const {fetchRequest} = useContext(AppContext);
  const history = useHistory();
  const location = useLocation();
  const [showModal, setShowModal] = useState(false);
  const urlArrays = location.pathname.split("/");
  const itemType = urlArrays[urlArrays.length - 1];

  const url = new URL(window.location.href)
  const params = new URLSearchParams(url.search);
  const templId = params.get('templ_id');

  const [showAlert, setShowAlert] = useState(false);
  const [successAlert, setSuccessAlert] = useState(true);
  const [alertMsg, setAlertMsg] = useState('');

  const [templateName, setTemplateName] = useState('');
  const [listFields, setListFields] = useState([]);
  const [listChosenFields, setListChosenFields] = useState([]);
  const [listMandatoryFields, setListMandatoryFields] = useState([]);
  const [listTransFuncs, setListTransFuncs] = useState([]);

  const [listMatchFields, setListMatchFields] = useState([]);
  const [listMatchFuncs, setListMatchFuncs] = useState([]);

  TabTitle(`Template - ${itemType}`);

  useEffect(() => {
    fetchRequest(`data/get-detail-template/${itemType}/${templId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setTemplateName(data.templateName);
          setListFields(data.listFields);
          setListTransFuncs(data.listTransFuncs);
          setListMatchFields(data.listMatchFields);
          setListChosenFields(data.listFields);
          setListMatchFuncs(data.listMatchFuncs);
          setListMandatoryFields(data.listMandatoryFields);
        }
      }
    }).catch((err) => alert(err));
  }, []);

  const handleOpenModal = (e) => {
    e.preventDefault();
    let notNullArray = listMatchFields.filter(element => element !== '');

    if (listMatchFields.every(element => element === null)) {
      setAlertValue(true, false, `You have not matched fields yet`)
    } else if (notNullArray.length && notNullArray.length > new Set(notNullArray).size) {
      setAlertValue(true, false, `Duplicate column names`)
    } else if (!listMandatoryFields.every(element => listChosenFields.includes(element))) {
      setAlertValue(true, false, `The following fields need to be matched (${listMandatoryFields.toString()})`)
    } else if (!listMatchFields.every(element => element === '')) {
        setShowModal(true);
    }
  };

  const handleCloseModal = () => {setShowModal(false)};

  const handleImportFile = (e) => {
    e.stopPropagation();
    e.preventDefault();

    fetchRequest(`data/update-matching-template/${itemType}/${templId}`, 'POST', 
    JSON.stringify({
      templateId: templId,
      templateName: templateName,
      listFields: listFields,
      matchFields: listMatchFields,
      matchFuncs: listMatchFuncs,
    }), false)
    .then((result) => {
      if (result != undefined) {
        if (result.status == 200) {
          setAlertValue(true, true, result.message);
          setTemplateName('');
          setListMatchFields([]);
          setListMatchFuncs([]);
        } else {
          setAlertValue(true, false, result.message)
        }
      }
    }).catch((err) => alert(err));
  };

  const setAlertValue = (isShow, isSuccess, msg) => {
    setShowAlert(isShow);
    setSuccessAlert(isSuccess);
    setAlertMsg(msg);
    setTimeout(() => {
      handleCloseAlert();
      if (isSuccess) {
        history.push(`/data-management/matching-template/${itemType}`)
      }
    }, 3000)
  }

  const handleMatchFields = (value, index) => {
    var matchFields = listMatchFields
    var chosenFields = listChosenFields
    if (!matchFields.length) {
      matchFields = Array(listFields.length).fill('');
      chosenFields = Array(listFields.length).fill('');
    }

    matchFields[index] = value;
    chosenFields[index] = value ? listFields[index] : '';
    setListMatchFields([...matchFields]);
    setListChosenFields([...chosenFields]);
  }

  const handleMatchFuncs = (value, index) => {
    var matchFields = listMatchFuncs
    if (!matchFields.length) {
      matchFields = Array(listFields.length).fill('');
    }

    matchFields[index] = value;
    setListMatchFuncs([...matchFields]);
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
            <h1 className="h2">Template - {itemType}</h1>
          </Col>
        </Row>
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
          <Col xs={12} className="mb-4">
          <Form className="row" onSubmit={(e) => handleOpenModal(e)}>
                <Form.Group className="mb-3 col-6">
                    <Form.Label>Template's name</Form.Label>
                    <Form.Control 
                        type="text"
                        value={templateName}
                        onChange={e => setTemplateName(e.target.value)}
                        required
                    />
                </Form.Group>
                <div className="row">   
                    <div className="col text-center">
                        <React.Fragment>
                        <Button variant="primary" className="m-1" type="submit">
                            Update
                        </Button>
                        <Modal
                            as={Modal.Dialog}
                            centered
                            show={showModal}
                            onHide={handleCloseModal}
                        >
                            <Modal.Header>
                            <Modal.Title className="h6">Import</Modal.Title>
                            <Button
                                variant="close"
                                aria-label="Close"
                                onClick={handleCloseModal}
                            />
                            </Modal.Header>
                            <Modal.Body>
                            <p>Do you want to import this template?</p>
                            </Modal.Body>
                            <Modal.Footer>
                            <Button
                                variant="secondary"
                                onClick={(e) => {
                                handleCloseModal();
                                handleImportFile(e);
                                }}
                            >
                                Yes
                            </Button>
                            <Button
                                variant="link"
                                className="text-gray ms-auto"
                                onClick={handleCloseModal}
                            >
                                No
                            </Button>
                            </Modal.Footer>
                        </Modal>
                        </React.Fragment>
                    </div>
                </div>  
              </Form>
          </Col>
        </Row>
        <Alert show={showAlert} variant={successAlert ? 'success' : 'danger'}>
          <Alert.Heading>{alertMsg}</Alert.Heading>
        </Alert>
        {listFields.length > 0 ? (
          <Card className="mb-4">
          <Card.Body>
          <Table striped hover responsive style={{backgroundColor: "white"}}>
            <thead className="thead-light">
              <tr>
                <th>ID</th>
                <th>Model Fields</th>
                <th>Column Names in File</th>
                <th>Transform Function</th>
              </tr>
            </thead>
            <tbody>
              {
                listFields.map((key, index) => 
                  <tr key={index}>
                    <td className="border-0 fw-bold">{index}</td>
                    <td className="border-0 fw-bold">{key}</td>
                    <td className="border-0 fw-bold">
                      <Form.Control
                        type="text"
                        value={listMatchFields.length ? listMatchFields[index] : ''}
                        onChange={(e) => {handleMatchFields(e.target.value, index)}}
                        required
                      >
                      </Form.Control>
                    </td>
                    <td className="border-0 fw-bold">
                    <Form.Control
                      as="select"
                      value={listMatchFuncs.length ? listMatchFuncs[index] : ''}
                      onChange={(e) => {handleMatchFuncs(e.target.value, index)}}
                      required
                    >
                      {listTransFuncs.map((item, index) => (
                        <option value={item} key={index}>
                          {item}
                        </option>
                      ))}
                    </Form.Control>
                    </td>
                  </tr>
                )
              }
            </tbody>
          </Table>
            </Card.Body>
          </Card>
        ) : (
          <></>
        )}
      </Container>
    </article>
  );
};
