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
import _ from "lodash";
import { v4 } from "uuid";

const findPathName = (path, index, attributeName) => {
  var pathName = "";

  if (index !== undefined) {
    pathName = path + ".value[" + index.toString() + "]";
  } else {
    if (path)
      pathName =
        attributeName === "connectedAttributes"
          ? path + ".connectedAttributes"
          : path + ".attributes." + attributeName;
    else if (attributeName)
      pathName =
        attributeName === "connectedAttributes"
          ? "connectedAttributes"
          : "attributes." + attributeName;
    else pathName = "";
  }

  return pathName;
};

const FormElement = ({
  path,
  index,
  formInfo,
  attributeName,
  formName,
  handleChangeValue,
  handleAddElement,
  handleRemoveElement,
  isLabel = true,
}) => {
  const order = index !== undefined ? "[" + (index + 1).toString() + "]" : "";
  const labelName = attributeName ? attributeName + order : formName + order;
  const pathName = findPathName(path, index, attributeName);
  const cloneObj = formInfo.elementAttributes
    ? JSON.parse(JSON.stringify(formInfo.elementAttributes))
    : {};

  if (attributeName === "id") {
    return <></>;
  } else if (formInfo.type === "object") {
    return (
      <Row>
        {isLabel ? (
          <Form.Label className="mt-4">{labelName.toUpperCase()}</Form.Label>
        ) : (
          <></>
        )}
        {Object.keys(formInfo.attributes).map((key, index) => (
          <FormElement
            path={pathName}
            attributeName={key}
            formInfo={formInfo.attributes[key]}
            key={index}
            handleChangeValue={handleChangeValue}
            handleAddElement={handleAddElement}
            handleRemoveElement={handleRemoveElement}
          />
        ))}
        {formInfo.connectedAttributes ? (
          <FormElement
            path={pathName}
            attributeName="connectedAttributes"
            formInfo={formInfo.connectedAttributes}
            handleChangeValue={handleChangeValue}
            handleAddElement={handleAddElement}
            handleRemoveElement={handleRemoveElement}
            isLabel={false}
          />
        ) : (
          <></>
        )}
      </Row>
    );
  } else if (formInfo.type === "text") {
    return (
      <Form.Group className="mb-3 col-6">
        <Form.Label>{labelName}</Form.Label>
        <Form.Control
          type="text"
          defaultValue={formInfo.value}
          onChange={(e) => handleChangeValue(pathName, e.target.value)}
        />
      </Form.Group>
    );
  } else if (formInfo.type === "integer" || formInfo.type === "decimal") {
    return (
      <Form.Group className="mb-3 col-6">
        <Form.Label>{labelName}</Form.Label>
        <Form.Control
          type="number"
          defaultValue={formInfo.value}
          min={0}
          max={formInfo.max ? formInfo.max : ""}
          step={formInfo.type === "integer" ? "1" : "any"}
          onChange={(e) => handleChangeValue(pathName, e.target.value)}
        />
      </Form.Group>
    );
  } else if (formInfo.type === "textarea") {
    return (
      <Form.Group className="mb-3 col-6">
        <Form.Label>{labelName}</Form.Label>
        <Form.Control
          as="textarea"
          defaultValue={formInfo.value}
          rows={5}
          onChange={(e) => handleChangeValue(pathName, e.target.value)}
        />
      </Form.Group>
    );
  } else if (formInfo.type === "datetime" || formInfo.type === "date") {
    return (
      <Form.Group className="mb-3 col-6">
        <Form.Label>{labelName}</Form.Label>
        <Form.Control
          type={formInfo.type}
          defaultValue={formInfo.value}
          min={formInfo.min ? formInfo.min : ""}
          max={formInfo.max ? formInfo.max : ""}
          onChange={(e) => handleChangeValue(pathName, e.target.value)}
        />
      </Form.Group>
    );
  } else if (formInfo.type === "select") {
    return (
      <Form.Group className="mb-3 col-6">
        <Form.Label>{labelName}</Form.Label>
        <Form.Control
          as="select"
          value={formInfo.value}
          onChange={(e) => handleChangeValue(pathName, e.target.value)}
        >
          <option value="">Open this select menu</option>
          {formInfo.choices.map((item, index) => (
            <option value={item} key={index}>
              {item}
            </option>
          ))}
        </Form.Control>
      </Form.Group>
    );
  } else if (formInfo.type === "m2m" || formInfo.type === "o2m") {
    return (
      <>
        {formInfo.value.map((value, index) =>
          value.status !== "removed" ? (
            <Row key={value.id}>
              <FormElement
                formInfo={value}
                index={index}
                path={pathName}
                handleChangeValue={handleChangeValue}
                attributeName={attributeName}
                handleAddElement={handleAddElement}
              />
              <div className="col-12 text-center">
                <Button
                  variant="primary"
                  className="m-1"
                  onClick={() => handleRemoveElement(pathName, index)}
                >{`Delete`}</Button>
              </div>
            </Row>
          ) : (
            <></>
          )
        )}
        <Row>
          <div className="col">
            <Button
              variant="primary"
              className="m-1"
              onClick={() => handleAddElement(pathName, cloneObj)}
            >{`+ ADD ${attributeName.toUpperCase()}`}</Button>
          </div>
        </Row>
      </>
    );
  } else {
    return <></>;
  }
};

export default () => {
  const { fetchRequest } = useContext(AppContext);
  const history = useHistory();
  const location = useLocation();
  const [formInfo, setFormInfo] = useState({});
  const [showDefault, setShowDefault] = useState(false);
  const [formState, setFormState] = useState(0);
  const urlArrays = location.pathname.split("/");
  const itemType = urlArrays[urlArrays.length - 2];
  const id = urlArrays[urlArrays.length - 1];

  TabTitle(`${id === "form" ? "New" : "Form"} ${itemType}`);

  useEffect(() => {
    fetchRequest(`dimadb/get-item/${itemType}/${id}`, "GET")
      .then((data) => {
        console.log(data)
        setFormInfo(data);
      })
      .catch((err) => alert(err));
  }, []);

  const handleOpenModal = (e, index) => {
    e.preventDefault();
    setFormState(index);
    setShowDefault(true);
  };

  const handleClose = () => setShowDefault(false);

  const handleChangeValue = (path, value) => {
    console.log(path);
    const pathValue = path + ".value";
    const cloneFormInfo = { ...formInfo };

    _.set(cloneFormInfo, pathValue, value);
    setFormInfo(cloneFormInfo);
  };

  const handleAddElement = (path, obj) => {
    const pathValue = path + ".value";
    var cloneFormInfo = { ...formInfo };

    const oldArray = _.get(cloneFormInfo, pathValue);
    var cloneOldArray = [...oldArray];
    obj.id = v4();

    cloneOldArray.push(obj);
    _.set(cloneFormInfo, pathValue, cloneOldArray);
    setFormInfo(cloneFormInfo);
  };

  const handleRemoveElement = (path, index) => {
    const pathValue = path + ".value";
    var cloneFormInfo = { ...formInfo };

    const oldArray = _.get(cloneFormInfo, pathValue);
    var cloneOldArray = [...oldArray];

    cloneOldArray[index]["status"] = "removed";
    _.set(cloneFormInfo, pathValue, cloneOldArray);
    setFormInfo(cloneFormInfo);
  };

  const handleSendForm = (e) => {
    e.preventDefault();

    fetchRequest(
      `dimadb/get-item/${itemType}/${id}/`,
      id === "form" ? "POST" : "PUT",
      JSON.stringify(formInfo)
    )
      .then((data) => {
        alert(
          `${id === "form" ? "Create new" : "Update"} ${itemType} successfully`
        );
        if (id === "form") {
          history.go(-1);
        } else {
          history.go(0);
        }
      })
      .catch((err) => alert(err));
  };

  const handleDeleteForm = (e) => {
    fetchRequest(
      `dimadb/get-item/${itemType}/${id}/`,
      "DELETE",
      JSON.stringify(formInfo)
    )
      .then((data) => {
        alert(`Delete ${itemType} successfully`);
        history.go(-1);
      })
      .catch((err) => alert(err));
  };

  return (
    <article>
      <Container className="px-0">
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center pt-3">
          <Col className="d-block mb-2 mb-md-0">
            <h1 className="h2">Form</h1>
          </Col>
        </Row>
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
          <Col xs={12} className="mb-4">
            {!_.isEmpty(formInfo) ? (
              <Form className="row" onSubmit={(e) => handleOpenModal(e, 0)}>
                <FormElement
                  formInfo={formInfo}
                  handleChangeValue={handleChangeValue}
                  formName={"event"}
                  handleAddElement={handleAddElement}
                  handleRemoveElement={handleRemoveElement}
                />
                <div className="row">
                  {id === "form" ? (
                    <div className="col text-center">
                      <React.Fragment>
                        <Button variant="primary" className="m-1" type="submit">
                          Save
                        </Button>
                        <Modal
                          as={Modal.Dialog}
                          centered
                          show={showDefault}
                          onHide={handleClose}
                        >
                          <Modal.Header>
                            <Modal.Title className="h6">Save</Modal.Title>
                            <Button
                              variant="close"
                              aria-label="Close"
                              onClick={handleClose}
                            />
                          </Modal.Header>
                          <Modal.Body>
                            <p>Do you want to save this {itemType} ?</p>
                          </Modal.Body>
                          <Modal.Footer>
                            <Button
                              variant="secondary"
                              onClick={(e) => {
                                handleClose();
                                handleSendForm(e);
                              }}
                            >
                              Yes
                            </Button>
                            <Button
                              variant="link"
                              className="text-gray ms-auto"
                              onClick={handleClose}
                            >
                              No
                            </Button>
                          </Modal.Footer>
                        </Modal>
                      </React.Fragment>
                    </div>
                  ) : (
                    <div className="col text-center">
                      <React.Fragment>
                        <Button variant="primary" className="m-1" type="submit">
                          Update
                        </Button>
                        <Button
                          variant="secondary"
                          className="m-1"
                          onClick={(e) => handleOpenModal(e, 1)}
                        >
                          Delete
                        </Button>
                        <Modal
                          as={Modal.Dialog}
                          centered
                          show={showDefault}
                          onHide={handleClose}
                        >
                          <Modal.Header>
                            <Modal.Title className="h6">
                              {formState ? "Delete" : "Update"}
                            </Modal.Title>
                            <Button
                              variant="close"
                              aria-label="Close"
                              onClick={handleClose}
                            />
                          </Modal.Header>
                          <Modal.Body>
                            <p>
                              Do you want to {formState ? "delete" : "update"}{" "}
                              {itemType} {id} ?
                            </p>
                          </Modal.Body>
                          <Modal.Footer>
                            <Button
                              variant="secondary"
                              onClick={(e) => {
                                handleClose();
                                if (formState) {
                                  handleDeleteForm(e);
                                } else {
                                  handleSendForm(e);
                                }
                              }}
                            >
                              Yes
                            </Button>
                            <Button
                              variant="link"
                              className="text-gray ms-auto"
                              onClick={handleClose}
                            >
                              No
                            </Button>
                          </Modal.Footer>
                        </Modal>
                      </React.Fragment>
                    </div>
                  )}
                </div>
              </Form>
            ) : (
              <></>
            )}
          </Col>
        </Row>
      </Container>
    </article>
  );
};
