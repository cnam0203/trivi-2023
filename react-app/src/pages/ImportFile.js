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

  const [showAlert, setShowAlert] = useState(false);
  const [successAlert, setSuccessAlert] = useState(true);
  const [alertMsg, setAlertMsg] = useState('');

  const [listFields, setListFields] = useState([]);
  const [listMandatoryFields, setListMandatoryFields] = useState([]);
  const [listTemplates, setListTemplates] = useState([]);
  const [listTransFuncs, setListTransFuncs] = useState([]);

  const [listMatchFields, setListMatchFields] = useState([]);
  const [listMatchFuncs, setListMatchFuncs] = useState([]);

  const { CSVReader } = useCSVReader();


  const [items, setItems] = useState([]);
  const [searchItems, setSearchItems] = useState([]);
  const columns = searchItems.length
    ? Object.keys(searchItems[0]).map((key) => {
        return { Header: key, accessor: key };
      })
    : [];

  TabTitle(`Import File - ${itemType}`);

  useEffect(() => {
    fetchRequest(`data/get-import-file-info/${itemType}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        setListFields(data.listFields);
        setListTransFuncs(data.transFuncs);
        setListMandatoryFields(data.mandatoryFields);
        setListTemplates(data.templates)
      }
    }).catch((err) => alert(err));
  }, []);

  const handleOpenModal = (e) => {
    e.preventDefault();

    if (!items.length) {
      setAlertValue(true, false, `There is no data`)
    }else if (listMatchFields.every(element => element === null)) {
      setAlertValue(true, false, `You have not matched fields yet`)
    } else if (!listMandatoryFields.every(element => listMatchFields.includes(element))) {
      setAlertValue(true, false, `The following fields need to be matched (${listMandatoryFields.toString()})`)
    } else if (!listMatchFields.every(element => element === '')) {
        setShowModal(true);
    } 
  };

  const setAllItems = (json, level = 2) => {
    if (level >= 2) setItems(json);
    if (level >= 1) setSearchItems(json);
  };

  const handleCloseModal = () => {setShowModal(false)};

  const handleImportFile = (e) => {
    e.stopPropagation();
    e.preventDefault();

    fetchRequest(`data/import-csv-file/${itemType}`, 'POST', 
    JSON.stringify({
      data: searchItems,
      columns: columns,
      matchFields: listMatchFields,
      matchFuncs: listMatchFuncs,
      isOverwrite: true,
    }), false)
    .then((result) => {
      if (result != undefined) {
        let msg = '';
        msg += `Total rows: ${result.totalData} \n`
        msg += `Total inserted rows: ${result.totalInsert} \n`
        msg += `Total overwrited rows: ${result.totalOverwrite} \n`
        msg += `Total error rows: ${result.errors.length} \n`
        msg += `List errors:  \n`
        msg += result.errors.slice(0, 10).map(err => `${err} \n`)
        msg += '...'

        if (result.errors.length) {
          setAlertValue(true, false, msg, 10000)
        } else {
          setAlertValue(true, true, msg)
        }
      }
    }).catch((err) => alert(err));
  };

  const handleFormatData = (results) => {
    const data = results.data
    if (data.length > 0) {
      const columns = data[0].map(key => {return key});
      var rows = [];

      for (let i = 1; i < data.length; i++) {
        var newRow = {}
        data[i].map((key, index) => {
          newRow[columns[index]] = key
        });
        rows.push(newRow);
      }

      setAllItems(rows);
    }
  }

  const setAlertValue = (isShow, isSuccess, msg, time=3000) => {
    setShowAlert(isShow);
    setSuccessAlert(isSuccess);
    setAlertMsg(msg);
    setTimeout(() => {
      handleCloseAlert();
      if (isSuccess) {
        history.push(`/data-management/list/${itemType}`)
      }
    }, time)
  }

  const handleMatchFields = (value, index) => {
    var matchFields = listMatchFields
    if (!matchFields.length) {
      matchFields = Array(columns.length).fill('');
    }

    if (matchFields.includes(value) && value != '') {
      setAlertValue(true, false, `${value} field is already matched`)
    } else {
      matchFields[index] = value;
      setListMatchFields([...matchFields]);
    }
  }

  const handleMatchFuncs = (value, index) => {
    var matchFields = listMatchFuncs
    if (!matchFields.length) {
      matchFields = Array(columns.length).fill('');
    }

    matchFields[index] = value;
    setListMatchFuncs([...matchFields]);
  }

  const handleCloseAlert = () => {
    setShowAlert(false);
    setSuccessAlert(true);
    setAlertMsg('');
  }

  const handleChooseTemplate = (value) => {
    if (value == 'none') {
      setListMatchFields([])
      setListMatchFuncs([])
    } else {
      const template = listTemplates[value];
      const fields = template['listMatchFields'];

      let matchFields = []
      let matchFuncs = []
      for (let index=0; index < columns.length; index++) {
        const columnName = columns[index]['Header'];
        if (columnName in fields) {
          let modelField = fields[columnName]['modelField']
          let func = fields[columnName]['func']
          
          matchFields[index] = modelField;
          matchFuncs[index] = func;
        } else {
          matchFields[index] = '';
          matchFuncs[index] = '';
        }
      }

      setListMatchFields([...matchFields]);
      setListMatchFuncs([...matchFuncs]);
    }
  }

  return (
     <CSVReader
      onUploadAccepted={(results) => {
        handleFormatData(results);
      }}
      config={{skipEmptyLines: true}}
    >
      {({
        getRootProps,
        acceptedFile,
        ProgressBar,
        getRemoveFileProps,
      }) => (
    <article>
      <Container className="px-0">
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center pt-3">
          <Col className="d-block mb-2 mb-md-0">
            <h1 className="h2">Import File - {itemType}</h1>
          </Col>
        </Row>
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
          <Col xs={12} className="mb-4">
          <Form className="row" onSubmit={(e) => handleOpenModal(e)}>
                <Form.Group className="mb-3 col-6">
                    <Form.Label>Upload File</Form.Label>
                    <Form.Control 
                        type="text"
                        value={acceptedFile ? acceptedFile.name : "Choose a .csv file"}
                        // onClick={() => handleChooseFile()}
                        {...getRootProps()}
                        readOnly
                    />
                </Form.Group>
                {
                    columns.length && listTemplates.length ? 
                    <Form.Group className="mb-3 col-6">
                        <Form.Label>Mapping templates</Form.Label>
                        <Form.Control
                        as="select"
                        defaultValue={''}
                        onChange={(e) => handleChooseTemplate(e.target.value)}
                        required
                        >
                        <option value="none">Open this select menu</option>
                        {listTemplates.map((item, index) => (
                            <option value={index} key={index}>
                                {item.name}
                            </option>
                        ))}
                        </Form.Control>
                    </Form.Group>  : <></>
                }
                <div className="row">   
                    <div className="col text-center">
                        <React.Fragment>
                        <Button variant="primary" className="m-1" type="submit">
                            Import
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
                            <p>Do you want to import this file into {itemType}?</p>
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
        {columns.length ? (
          <Card className="mb-4">
          <Card.Body>
          <Table striped hover responsive style={{backgroundColor: "white"}}>
            <thead className="thead-light">
              <tr>
                <th>ID</th>
                <th>File Columns</th>
                <th>Model Fields</th>
                <th>Transform Function</th>
              </tr>
            </thead>
            <tbody>
              {
                columns.map((key, index) => 
                  <tr key={index}>
                    <td className="border-0 fw-bold">{index}</td>
                    <td className="border-0 fw-bold">{key.Header}</td>
                    <td className="border-0 fw-bold">
                    <Form.Control
                      as="select"
                      value={listMatchFields.length ? listMatchFields[index] : ''}
                      onChange={(e) => {handleMatchFields(e.target.value, index)}}
                      required
                    >
                      <option value="">Select a field</option>
                      {listFields.map((item, index) => (
                        <option value={item} key={index}>
                          {item}
                        </option>
                      ))}
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
        {columns.length > 0 ? (
          <ProcessTables
            columns={columns}
            data={searchItems.slice(0, 20)}
            clickTitle={false}
            isShowPagnition={false}
          />
        ) : (
          <></>
        )}
      </Container>
    </article>)}
    </CSVReader>
  );
};
