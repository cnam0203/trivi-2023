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
import Highcharts from "highcharts";

const CustomerSegmentForm = ({itemType, itemId, setAlertValue}) => {
  const {fetchRequest} = useContext(AppContext);
  const [info, setInfo] = useState({});
  const [name, setName] = useState('');
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    fetchRequest(`knowledge/get-model-info/${itemType}/${itemId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setInfo(data.info);
          setName(data.info.model_name);
          setClusters(data.info.clusters);
        }
      }
    }).catch((err) => alert(err));
  }, []);

  const handleNameChange = (event) => {
    setName(event.target.value);
  }

  const handleClusterNameChange = (event, index) => {
    const updatedClusters = [...clusters];
    updatedClusters[index].name = event.target.value;
    setClusters(updatedClusters);
  }

  const handleFormSubmit = (event) => {
    event.preventDefault();
    const updatedInfo = {
      ...info,
      name,
      clusters,
    };
    // Call API to update user object information
    fetchRequest(`knowledge/update-model/${itemType}/${itemId}`, 'POST', 
    JSON.stringify(updatedInfo))
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAlertValue(true, true, 'Update successfully')
        }
      }
    }).catch((err) => alert(err));
  }

  useEffect(() => {
    if ('labels' in info) {
      createChart();
    }}, [info]
  )
  
  function createChart() {
    const data = info['labels'].map((point, index) => ({
      'x': parseFloat(point.x),
      'y': parseFloat(point.y),
      'name': (point.label).toString(),
      'cluster': (point.label).toString(),
      'index': index
    }));
    
    const clusters = [...new Set(data.map(point => point.cluster))]; // get unique clusters
    const colors = Highcharts.getOptions().colors.slice(0, clusters.length); // get colors for each cluster
    
    const seriesData = clusters.map((cluster, index) => ({
      name: `Cluster ${cluster}`,
      data: data.filter(point => point.cluster === cluster),
      color: colors[index],
    }));
    
    Highcharts.chart('chart-container', {
      chart: {
        type: 'scatter',
      },
      title: {
        text: 'Clustering Chart',
      },
      xAxis: {
        title: {
          text: 'X Axis',
        },
      },
      yAxis: {
        title: {
          text: 'Y Axis',
        },
      },
      plotOptions: {
        scatter: {
          marker: {
            radius: 5,
          },
          states: {
            hover: {
              enabled: true,
              lineColor: 'rgb(100,100,100)',
            },
          },
          tooltip: {
            headerFormat: '<b>{point.name}</b>',
            pointFormat: 'Cluster: {point.name} <br> ID: {point.index} <br> {point.x}, {point.y}',
          },
        },
      },
      series: seriesData,
    });
  }

  return (
    <Form className="row" onSubmit={handleFormSubmit}>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Name: </Form.Label>
        <Form.Control type="text" value={name} onChange={handleNameChange} />
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Number of cluster: </Form.Label>
        <Form.Control type="text" value={info.num_clusters} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data from: </Form.Label>
        <Form.Control type="text" value={info.start_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data to:</Form.Label>
        <Form.Control type="text" value={info.end_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Run at: </Form.Label>
        <Form.Control type="text" value={info.run_at} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Fields to info: </Form.Label>
        <Form.Control type="text" value={info.fields} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>API used for customer segmentation:</Form.Label>
        <Form.Control type="text" value={info.api} readOnly/>
      </Form.Group>
      <Form.Group controlId="formJobs">
        <Form.Label>Cluster:</Form.Label>
        {clusters.map((cluster, index) => (
          <Card key={index} style={{marginBottom: '10px', padding: '10px'}}>
            <Form.Text type="text" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{`Cluster ${index}`}</Form.Text>
              <div className="row"> 
              <Form.Group className="mb-3 col-6">
                <Form.Label>Cluster name:</Form.Label>
                <Form.Control type="text" value={cluster.name} onChange={(event) => handleClusterNameChange(event, index)} />
              </Form.Group>
              <Form.Group className="mb-3 col-6">
                <Form.Label>Number of customers:</Form.Label>
                <Form.Control type="text" value={cluster.count} readOnly/>
              </Form.Group>
            </div>
            <Form.Text type="text" style={{ fontSize: '1.1rem' }}>{`Centroid`}</Form.Text>
            <div className="row"> 
            {
              Object.keys(cluster.centroid).map((key, index )=> (
                <Form.Group className="mb-3 col-6" key={index}>
                  <Form.Label>{key}:</Form.Label>
                  <Form.Control type="text" value={cluster.centroid[key]} readOnly/>
                </Form.Group>
              ))
            }
            </div>
          </Card>
        ))}
      </Form.Group>
      <div className="row"> 
        <div className="col text-center">
          <Button variant="primary" type="submit" className="m-1">
            Save
          </Button>
        </div>
      </div>
      <Card style={{margin: '15px', padding: '10px'}}>
        <div id="chart-container" style={{marginTop: 50}}></div>
      </Card>
      {
        'labels' in info ? 
        <PageCustomizedTable info={{'title': 'Cluster samples', 'data': info['labels']}} width={12} isShowHeader={true}/> : <></>
      }
    </Form>
  );
}

const RecommendationForm = ({itemType, itemId, setAlertValue}) => {
  const {fetchRequest} = useContext(AppContext);
  const [info, setInfo] = useState({});
  const [name, setName] = useState('');

  useEffect(() => {
    fetchRequest(`knowledge/get-model-info/${itemType}/${itemId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setInfo(data.info)
          setName(data.info.model_name)
        }
      }
    }).catch((err) => alert(err));
  }, []);

  const handleNameChange = (event) => {
    setName(event.target.value);
  }


  const handleFormSubmit = (event) => {
    event.preventDefault();
    const updatedInfo = {
      ...info,
      name,
    };
    // Call API to update user object information
    fetchRequest(`knowledge/update-model/${itemType}/${itemId}`, 'POST', 
    JSON.stringify(updatedInfo))
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAlertValue(true, true, 'Update successfully')
        }
      }
    }).catch((err) => alert(err));
  }

  return (
    <Form className="row" onSubmit={handleFormSubmit}>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Name: </Form.Label>
        <Form.Control type="text" value={name} onChange={handleNameChange} />
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Algorithm: </Form.Label>
        <Form.Control type="text" value={info.algorithm} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Min similarity score: </Form.Label>
        <Form.Control type="text" value={info.similarity_score} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Recommended threshold: </Form.Label>
        <Form.Control type="text" value={info.threshold} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>number of recommended products: </Form.Label>
        <Form.Control type="text" value={info.numbers} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data from: </Form.Label>
        <Form.Control type="text" value={info.start_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data to:</Form.Label>
        <Form.Control type="text" value={info.end_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Run at: </Form.Label>
        <Form.Control type="text" value={info.run_at} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Fields to info: </Form.Label>
        <Form.Control type="text" value={info.fields} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>API used for recommendation:</Form.Label>
        <Form.Control type="text" value={info.api} readOnly/>
      </Form.Group>
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

const AssociationRuleForm = ({itemType, itemId, setAlertValue}) => {
  const {fetchRequest} = useContext(AppContext);
  const [info, setInfo] = useState({});
  const [name, setName] = useState('');

  useEffect(() => {
    fetchRequest(`knowledge/get-model-info/${itemType}/${itemId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setInfo(data.info)
          setName(data.info.model_name)
        }
      }
    }).catch((err) => alert(err));
  }, []);

  const handleNameChange = (event) => {
    setName(event.target.value);
  }

  const handleFormSubmit = (event) => {
    event.preventDefault();
    const updatedInfo = {
      ...info,
      name,
    };
    // Call API to update user object information
    fetchRequest(`knowledge/update-model/${itemType}/${itemId}`, 'POST', 
    JSON.stringify(updatedInfo))
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAlertValue(true, true, 'Update successfully')
        }
      }
    }).catch((err) => alert(err));
  }

  return (
    <Form className="row" onSubmit={handleFormSubmit}>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Name: </Form.Label>
        <Form.Control type="text" value={name} onChange={handleNameChange} />
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Min support: </Form.Label>
        <Form.Control type="text" value={info.min_support} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Confidence threshold: </Form.Label>
        <Form.Control type="text" value={info.threshold} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Total itemsets found: </Form.Label>
        <Form.Control type="text" value={info.total_itemsets} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data from: </Form.Label>
        <Form.Control type="text" value={info.start_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data to:</Form.Label>
        <Form.Control type="text" value={info.end_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Run at: </Form.Label>
        <Form.Control type="text" value={info.run_at} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>API used for association-rule:</Form.Label>
        <Form.Control type="text" value={info.api} readOnly/>
      </Form.Group>
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

const CorrelationForm = ({itemType, itemId, setAlertValue}) => {
  const {fetchRequest} = useContext(AppContext);
  const [info, setInfo] = useState({});
  const [name, setName] = useState('');

  useEffect(() => {
    fetchRequest(`knowledge/get-model-info/${itemType}/${itemId}`, 'GET')
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setInfo(data.info)
          setName(data.info.model_name)
        }
      }
    }).catch((err) => alert(err));
  }, []);

  const handleNameChange = (event) => {
    setName(event.target.value);
  }

  const handleFormSubmit = (event) => {
    event.preventDefault();
    const updatedInfo = {
      ...info,
      name,
    };
    // Call API to update user object information
    fetchRequest(`knowledge/update-model/${itemType}/${itemId}`, 'POST', 
    JSON.stringify(updatedInfo))
    .then((data) => {
      if (data != undefined) {
        if (data.status == 200) {
          setAlertValue(true, true, 'Update successfully')
        }
      }
    }).catch((err) => alert(err));
  }

  return (
    <Form className="row" onSubmit={handleFormSubmit}>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Name: </Form.Label>
        <Form.Control type="text" value={name} onChange={handleNameChange} />
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Dimension: </Form.Label>
        <Form.Control type="text" value={info.dimension} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data from: </Form.Label>
        <Form.Control type="text" value={info.start_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Data to:</Form.Label>
        <Form.Control type="text" value={info.end_date} readOnly/>
      </Form.Group>
      <Form.Group className="mb-3 col-6">
        <Form.Label>Run at: </Form.Label>
        <Form.Control type="text" value={info.run_at} readOnly/>
      </Form.Group>
      <div className="row"> 
        <div className="col text-center">
          <Button variant="primary" type="submit" className="m-1">
            Save
          </Button>
        </div>
      </div>
      <Row className="d-flex flex-wrap flex-md-nowrap justify-content-center align-items-center py-3">
        {
          Object.keys(info).length ? 
            <PageCustomizedTable info={info.corr_coefficient} width={12} isShowHeader={true}/> : <></>
        }
      </Row>
      <Row className="d-flex flex-wrap flex-md-nowrap justify-content-center align-items-center py-3">
        {
          Object.keys(info).length ? 
          <img src={info.img_path} alt="Sample Image" width="20"/> : <></>
        }
      </Row>
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
  const itemType = urlArrays[urlArrays.length - 2];
  const itemId = urlArrays[urlArrays.length - 1];

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

  const handleAPIPage = () => {
    history.push(`/data-knowledge/test-api/${itemType}/${itemId}`)
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
            <h1 className="h2">Model - {itemType}</h1>
          </Col>
          <Col className="d-block mb-2 mb-md-0 text-right">
            <Button variant="primary" className="m-1 mr-3" onClick={handleAPIPage}>
              Test API
            </Button>
          </Col>
        </Row>
        <Alert show={showAlert} variant={successAlert ? 'success' : 'danger'}>
          <Alert.Heading>{alertMsg}</Alert.Heading>
        </Alert>
        <Card className="mb-2">
          <Card.Body>
          <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-3">
            {(() => {
              switch(itemType) {
                case 'customer-segmentation':
                  return <CustomerSegmentForm itemType={itemType} itemId={itemId} setAlertValue={setAlertValue} />;
                case 'product-recommendation':
                  return <RecommendationForm itemType={itemType} itemId={itemId} setAlertValue={setAlertValue} />;
                case 'association-rule':
                  return <AssociationRuleForm itemType={itemType} itemId={itemId} setAlertValue={setAlertValue} />;
                case 'correlation':
                  return <CorrelationForm itemType={itemType} itemId={itemId} setAlertValue={setAlertValue} />;
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
