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


const FieldsConfig = ({itemType, setAlertValue}) => {
  const {fetchRequest} = useContext(AppContext);
  const [algorithm, setAlgorithm] = useState('');
  const [inputs, setInputs] = useState([]);
  const [config, setConfig] = useState([]);

  useEffect(() => {
    fetchRequest(`knowledge/get-model-config/${itemType}`, 'GET')
      .then((data) => {
        if (data !== undefined && data.status === 200) {
          setConfig(data.config);
          setAlgorithm(data.config[0].id); // Set default algorithm state from fetched config
          setInputs(data.config[0].parameters); // Set default inputs state from fetched config
        }
      })
      .catch((err) => alert(err));
  }, []);

  const handleAlgorithmChange = (event) => {
    const selectedAlgorithm = event.target.value;
    const selectedConfig = config.find((item) => item.id === selectedAlgorithm);

    setAlgorithm(selectedAlgorithm);
    setInputs(selectedConfig ? selectedConfig.parameters : []);
  };

  const handleFormSubmit = (event) => {
    event.preventDefault();
    const formData = {};
    inputs.forEach((field) => {
      formData[field.id] = field.value;
    });
    formData['algorithm'] = algorithm;

    fetchRequest(`knowledge/run-model/${itemType}`, 'POST', 
      JSON.stringify(formData)
    )
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAlertValue(true, true, 'Build model successfully')
        } else {
          setAlertValue(true, false, 'Build model unsuccessfully')
        }
      }
    }).catch((err) => alert(err));
  };

  const handleInputChange = (event, inputId) => {
    const updatedInputs = [...inputs];
    // Find the input with the matching ID
    const input = updatedInputs.find(input => input.id === inputId);
    if (input) {
      // Update the input's value
      input.value = event.target.value;
      setInputs(updatedInputs);
    }
  };

    const renderField = (field) => {
    switch (field.type) {
      case 'integer':
        return (
          <Form.Group key={field.id} className="mb-3 col-6">
            <Form.Label>{field.label}</Form.Label>
            <Form.Control
              type="number"
              step="1"
              value={field.value}
              required
              onChange={(event) => handleInputChange(event, field.id)}
            />
          </Form.Group>
        );
      case 'float':
        return (
          <Form.Group key={field.id} className="mb-3 col-6">
            <Form.Label>{field.label}</Form.Label>
            <Form.Control
              type="number"
              required
              value={field.value}
              onChange={(event) => handleInputChange(event, field.id)}
            />
          </Form.Group>
        );
      case 'date':
        return (
          <Form.Group key={field.id} className="mb-3 col-6">
            <Form.Label>{field.label}</Form.Label>
            <Form.Control
              type="date"
              required
              value={field.value}
              onChange={(event) => handleInputChange(event, field.id)}
            />
          </Form.Group>
        );
      case 'select':
        return (
          <Form.Group key={field.id} className="mb-3 col-6">
            <Form.Label>{field.label}</Form.Label>
            <Form.Control
              as="select"
              required
              value={field.value}
              onChange={(event) => handleInputChange(event, field.id)}
            >
              {field.options.map((option, index) => (
                <option key={index} value={typeof option == 'object' ? option['id'] : option}>
                  {typeof option == 'object' ? option['label'] : option}
                </option>
              ))}
            </Form.Control>
          </Form.Group>
        );
      case 'multi-select':
        return (
          <Form.Group key={field.id} className="mb-3 col-6">
            <Form.Label>{field.label}</Form.Label>
            {field.options.map((option, index) => (
            <Form.Check
              key={index}
              type="checkbox"
              label={typeof option == 'object' ? option['label'] : option}
              checked={field.value.includes(typeof option == 'object' ? option['id'] : option)}
              onChange={(event) => {
                const newValue = [...field.value];
                if (event.target.checked) {
                  newValue.push(typeof option == 'object' ? option['id'] : option);
                } else {
                  const index = newValue.indexOf(typeof option == 'object' ? option['id'] : option);
                  if (index > -1) {
                    newValue.splice(index, 1);
                  }
                }
                handleInputChange({ target: { value: newValue } }, field.id);
              }}
            />
          ))}
          </Form.Group>
        );
      default:
        return (
          <Form.Group key={field.id} className="mb-3 col-6">
            <Form.Label>{field.label}</Form.Label>
            <Form.Control
              type="text"
              required
              value={field.value}
              onChange={(event) => handleInputChange(event, field.id)}
            />
          </Form.Group>
        );
    }
  };

  return (
    <Form className="row" onSubmit={handleFormSubmit}>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Algorithm</Form.Label>
        <Form.Control
          as="select"
          value={algorithm}
          onChange={(event) => {
            handleAlgorithmChange(event);
          }}
        >
          {config.map((item, index) => (
            <option key={index} value={item.id}>
              {item.name}
            </option>
          ))}
        </Form.Control>
      </Form.Group>
      {
        inputs ? 
        <>{inputs.map((field) => renderField(field))}</> : <></>
      }
      <div className="row"> 
        <div className="col text-center">
          <Button variant="primary" type="submit" className="m-1">
            Save
          </Button>
        </div>
      </div>
    </Form>
  );
}

export default () => {  
  const refFile = useRef(null);
  const {fetchRequest} = useContext(AppContext);
  const history = useHistory();
  const location = useLocation();
  const [showModal, setShowModal] = useState(false);
  const urlArrays = location.pathname.split("/");
  const itemType = urlArrays[urlArrays.length - 1];

  const [showAlert, setShowAlert] = useState(false);
  const [successAlert, setSuccessAlert] = useState(true);
  const [alertMsg, setAlertMsg] = useState('');

  TabTitle(`Model - ${itemType}`);

  const handleOpenModal = (e) => {
    e.preventDefault();
  };

  const handleCloseModal = () => {setShowModal(false)};

  const setAlertValue = (isShow, isSuccess, msg) => {
    setShowAlert(isShow);
    setSuccessAlert(isSuccess);
    setAlertMsg(msg);
    setTimeout(() => {
      handleCloseAlert();
      if (isSuccess) {
        history.push(`/data-knowledge/list/${itemType}`)
      }
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
            <h1 className="h2">New {itemType} model</h1>
          </Col>
        </Row>
        <Alert show={showAlert} variant={successAlert ? 'success' : 'danger'}>
          <Alert.Heading>{alertMsg}</Alert.Heading>
        </Alert>
        <Card className="mb-2">
          <Card.Body>
            <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
              <FieldsConfig itemType={itemType} setAlertValue={setAlertValue}/>
            </Row>
          </Card.Body>
        </Card>
      </Container>
    </article>
  );
};
