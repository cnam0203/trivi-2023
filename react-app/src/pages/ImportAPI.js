import React, { useState, useEffect, useContext } from "react";
import {
  Col,
  Row,
  Form,
  Container,
  Button,
  Modal,
} from "@themesberg/react-bootstrap";
import { useHistory, useLocation } from "react-router";
import { TabTitle } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";


export default () => {  
  const {fetchRequest} = useContext(AppContext);
  const history = useHistory();
  const location = useLocation();
  const urlArrays = location.pathname.split("/");
  const itemType = urlArrays[urlArrays.length - 1];
  const [instruction, setInstruction] = useState('');

  TabTitle(`Import API - ${itemType}`);

  useEffect(() => {
    fetchRequest(`data/get-import-api-info/${itemType}`, 'GET')
    .then((data) => {
      if (data != undefined) 
        console.log(data.fields)
        setInstruction(data.instruction);
    }).catch((err) => alert(err));
  }, []);

  return (
    <article>
      <Container className="px-0">
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center pt-3">
          <Col className="d-block mb-2 mb-md-0">
            <h1 className="h2">Import API - {itemType}</h1>
          </Col>
        </Row>
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
          <Col xs={12} className="mb-4">
            <Form.Group className="mb-3 col-12">
                <Form.Label>Example of Restful API</Form.Label>
                <Form.Control
                  as="textarea"
                  value={instruction}
                  readOnly
                  rows={50}
                >
                </Form.Control>
              </Form.Group>
          </Col>
        </Row>
      </Container>
    </article>
  );
};
