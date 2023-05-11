import React, { useState, useEffect, useContext } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearch } from "@fortawesome/free-solid-svg-icons";
import {
  Col,
  Row,
  Container,
  Button,
  Form,
  InputGroup,
  Modal,
  Alert
} from "@themesberg/react-bootstrap";
import { useHistory, useLocation } from "react-router";
import { CSVLink } from "react-csv";
import ProcessTables from "./tables/ProcessTables";
import { TabTitle, capitalize } from "../constants/generalFunctions";
import { AppContext } from "./AppContext";

export default () => {
  const {fetchRequest} = useContext(AppContext);
  const history = useHistory();
  const location = useLocation();
  const itemType = location.pathname.split("/").slice(-1)[0];
  const url = new URL(window.location.href)
  const params = new URLSearchParams(url.search);
  const importId = params.get('import_id');
  const [isViewDetail, setIsViewDetail] = useState(false);
  const [items, setItems] = useState([]);
  const [searchItems, setSearchItems] = useState([]);

  const [showModal, setShowModal] = useState(false);
  const [deleteItem, setDeleteItem] = useState('');

  const [showAlert, setShowAlert] = useState(false);
  const [successAlert, setSuccessAlert] = useState(true);
  const [alertMsg, setAlertMsg] = useState('');

  const headerKeys = searchItems.length
    ? Object.keys(searchItems[0]).map((key) => {
        return { label: key, key: key };
      })
    : [];
  const columns = searchItems.length
    ? Object.keys(searchItems[0]).map((key) => {
        return { Header: key, accessor: key };
      })
    : [];

  TabTitle(capitalize(itemType));

  useEffect(() => {
    fetchRequest(`data/get-list-view/${itemType}${importId ? `?import_id=${importId}` : ''}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        setAllItems(data.items);
        setIsViewDetail(data.isViewDetail);
      }
    }).catch((err) => alert(err));
  }, [itemType]);

  const setAllItems = (json, level = 2) => {
    if (level >= 2) setItems(json);
    if (level >= 1) setSearchItems(json);
  };

  const handleCloseModal = () => {
    setDeleteItem('');
    setShowModal(false);
  };

  const handleOpenModal = () => {setShowModal(true);};

  const handleDelete = (item) => {
    setDeleteItem(item);
    handleOpenModal();
  };

  const handleDeleteItem = () => {
    fetchRequest(`data/delete-item/${itemType}/${deleteItem}`, 'DELETE')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAlertValue(true, true, data.message)
        } else {
          setAlertValue(true, false, data.message)
        }
      }
    }).catch((err) => alert(err));
  }

  const setAlertValue = (isShow, isSuccess, msg, time=3000) => {
    setShowAlert(isShow);
    setSuccessAlert(isSuccess);
    setAlertMsg(msg);
    setTimeout(() => {
      handleCloseAlert();
      if (isSuccess) {
        history.go(0);
      }
    }, time)
  }

  const handleCloseAlert = () => {
    setShowAlert(false);
    setSuccessAlert(true);
    setAlertMsg('');
  }

  const handleViewDetail = (row) => {
    const id = row["id"];
    const url = `/data-management/detail/${itemType}/${id}`;
    history.push(url);
  };

  const handleImportFile = (e) => {
    const url = `/data-management/import-file/${itemType}`;
    history.push(url);
  };

  const handleImportAPI = (e) => {
    const url = `/data-management/import-api/${itemType}`;
    history.push(url);
  };

  const handleImportHistory = (e) => {
    const url = `/data-management/import-history/${itemType}`;
    history.push(url);
  };

  const handleOpenTemplate = (e) => {
    const url = `/data-management/matching-template/${itemType}`;
    history.push(url);
  };

  const handleNewItem = () => {
    const url = `/data-management/detail/${itemType}/form`;
    history.push(url);
  };

  const searchKeyWord = (keyword) => {
    if (keyword === "") {
      setAllItems(items, 2);
    } else {
      var filteredKeyWord = [];
      for (var i = 0; i < items.length; i++) {
        const obj = items[i];
        const keys = Object.keys(obj);
        for (var j = 0; j < keys.length; j++) {
          const value = String(obj[keys[j]]).toLowerCase();
          if (value.includes(keyword.toLowerCase())) {
            filteredKeyWord.push(obj);
            break;
          }
        }
      }
      setAllItems(filteredKeyWord, 1);
    }
  };
 
  return (
    <article>
      <Container className="px-0">
      <React.Fragment>
        <Modal
            as={Modal.Dialog}
            centered
            show={showModal}
            onHide={handleCloseModal}
        >
            <Modal.Header>
            <Modal.Title className="h6">Delete</Modal.Title>
            <Button
                variant="close"
                aria-label="Close"
                onClick={handleCloseModal}
            />
            </Modal.Header>
            <Modal.Body>
            <p>Do you want to delete this {itemType}?</p>
            </Modal.Body>
            <Modal.Footer>
            <Button
                variant="secondary"
                onClick={(e) => {
                handleCloseModal();
                handleDeleteItem();
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
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-4">
          <Col className="d-block mb-4 mb-md-0">
            <h1 className="h2">Tables</h1>
          </Col>
        </Row>
        <Row>
          <Col xs={9} className="mb-4">
            {/* {isViewDetail ? (
              <Button
                variant="primary"
                className="m-1"
                onClick={() => handleNewItem()}
              >
                New {itemType}
              </Button>
            ) : (
              <></>
            )} */}
            <Button
              variant="secondary"
              className="m-1"
              onClick={() => handleImportFile()}
            >
              Import File
            </Button>
            <Button
              variant="danger"
              className="m-1"
              onClick={() => handleImportAPI()}
            >
              Import API
            </Button>
            <Button variant="tertiary" className="m-1">
              <CSVLink data={searchItems} headers={headerKeys}>
                Export CSV
              </CSVLink>
            </Button>
            <Button
              variant="primary"
              className="m-1"
              onClick={() => handleImportHistory()}
            >
              Import history
            </Button>
            <Button
              variant="warning"
              className="m-1"
              onClick={() => handleOpenTemplate()}
            >
              Matching template
            </Button>
          </Col>
          <Col xs={3} className="mb-4">
            <Form.Group>
              <InputGroup className="input-group-merge">
                <Form.Control
                  type="text"
                  placeholder="Search a keyword"
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      searchKeyWord(e.target.value);
                    }
                  }}
                />
                <InputGroup.Text>
                  <FontAwesomeIcon
                    icon={faSearch}
                    style={{ cursor: "pointer" }}
                  />
                </InputGroup.Text>
              </InputGroup>
            </Form.Group>
          </Col>
        </Row>
        <Alert show={showAlert} variant={successAlert ? 'success' : 'danger'}>
          <Alert.Heading>{alertMsg}</Alert.Heading>
        </Alert>
        {columns.length > 0 ? (
          <ProcessTables
            isDeleteColumn={true}
            columns={columns}
            data={searchItems}
            isViewDetail={isViewDetail}
            handleViewDetail={handleViewDetail}
            handleDelete={handleDelete}
          />
        ) : (
          <></>
        )}
      </Container>
    </article>
  );
};
