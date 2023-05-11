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
  const [orgName, setOrgName] = useState('');
  const [orgDescript, setOrgDescript] = useState('');
  const [orgKey, setOrgKey] = useState('');
  const [showModal, setShowModal] = useState(false);
  const { fetchRequest } = useContext(AppContext);

  useEffect(() => {
    fetchRequest(
      `auth/get-org-info`,
      "GET",
    )
      .then((data) => {
        if (data.status == 200) {
          setOrgName(data.org_name);
          setOrgDescript(data.org_descript);
          setOrgKey(data.org_key);
        }
      })
      .catch((err) => alert(err));
  }, []);

  const handleGenerateKey = (e) => {
    e.preventDefault();
    fetchRequest(
      `auth/generate-secret-key`,
      "POST",
    )
      .then((data) => {
        if (data.status == 201) {
          alert(data.message)
        }
        else {
          alert(data.message);
          setOrgKey(data.org_key);
        }
      })
      .catch((err) => alert(err));
  }

  const handleChangeInfo = () => {
    fetchRequest(
      `auth/change-org-info`,
      "POST",
      JSON.stringify({
        orgName: orgName,
        orgDescript: orgDescript,
      })
    )
      .then((data) => {
        if (data.status == 201) {
          alert(data.message)
        }
        else {
          alert(data.message);
          setOrgName(data.org_name);
          setOrgDescript(data.org_descript);
        }
      })
      .catch((err) => alert(err));
  }

  const handleOpenModal = (e) => {
    e.preventDefault();
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <article>
      <Container className="px-0">
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center pt-3">
          <Col className="d-block mb-2 mb-md-0">
            <h1 className="h2">Organization</h1>
          </Col>
        </Row>
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
          <Form className="row" onSubmit={(e) => handleOpenModal(e)}>
            <Col xs={12} className="mb-4 d-flex align-items-center justify-content-center">
              <Form.Group className="mb-3 col-6">
                <Form.Label>Organization's Name</Form.Label>
                <Form.Control
                  required
                  type="text"
                  defaultValue={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col xs={12} className="mb-4 d-flex align-items-center justify-content-center">
              <Form.Group className="mb-3 col-6">
                <Form.Label>Description</Form.Label>
                <Form.Control
                  type="text"
                  defaultValue={orgDescript}
                  onChange={(e) => setOrgDescript(e.target.value)}
                  required
                />
              </Form.Group>
            </Col>
            <div className="row">
                  <div className="col text-center">
                    <React.Fragment>
                      <Button variant="primary" className="m-1" type="submit">
                        Change info
                      </Button>
                      <Modal
                        as={Modal.Dialog}
                        centered
                        show={showModal}
                        onHide={handleCloseModal}
                      >
                        <Modal.Header>
                          <Modal.Title className="h6">Submit</Modal.Title>
                          <Button
                            variant="close"
                            aria-label="Close"
                            onClick={handleCloseModal}
                          />
                        </Modal.Header>
                        <Modal.Body>
                          <p>
                            Do you want to change organization's info?
                          </p>
                        </Modal.Body>
                        <Modal.Footer>
                          <Button
                            variant="secondary"
                            onClick={(e) => {
                              handleCloseModal();
                              handleChangeInfo(e);
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
        </Row>
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
          <Form className="row" onSubmit={(e) => handleGenerateKey(e)}>
            <Col xs={12} className="mb-4 d-flex align-items-center justify-content-center">
              <Form.Group className="mb-3 col-6">
                <Form.Label>Secret Key</Form.Label>
                <Form.Control
                  required
                  readOnly
                  type="text"
                  defaultValue={orgKey}
                />
              </Form.Group>
            </Col>
            <div className="row">
                  <div className="col text-center">
                      <Button variant="primary" className="m-1" type="submit">
                        Generate Key
                      </Button>
                  </div>
                </div>
          </Form>
        </Row>
      </Container>
    </article>
  )
};
