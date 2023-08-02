import React, { useEffect, useContext, useState} from 'react';
import { AppContext } from "./AppContext";
import { useLocation } from 'react-router-dom';
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
import { PageCustomizedTable} from "../components/Tables";

const SearchResult = () => {
    const {fetchRequest} = useContext(AppContext);
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const searchQuery = searchParams.get('query');
    const [result, setResult] = useState({});

    useEffect(() => {
        console.log(searchQuery);
        fetchRequest(`knowledge/get-answer`, 'POST', 
            JSON.stringify({question: searchQuery})
        )
        .then((data) => {
            if (data != undefined) {
              if (data.status == 200) {
                console.log(data.data)
                setResult(data.data)
              } else {
                console.log(data)
                setResult(data.data)
              }
            }
          })
        .catch((err) => alert(err));
      }, [searchQuery]);

  return (
    <article>
      <Container className="px-0">
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center pt-3">
          <Col className="d-block mb-2 mb-md-0">
            <h1 className="h2">Answer</h1>
          </Col>
        </Row>
        <Card className="mb-2">
          <Card.Body>
          <Row className="d-flex flex-wrap flex-md-nowrap justify-content-center align-items-center py-3">
          {(() => {
              switch(result.type) {
                case 'text':
                  return (
                    <Form className="row">
                        <Form.Group className="mb-3 col-6">
                            <Form.Label>The answer is : </Form.Label>
                            <Form.Control type="text" value={result.data} readOnly />
                        </Form.Group>
                    </Form>
                  );
                case 'table':
                  return (
                    <PageCustomizedTable info={result.data} width={8} isShowHeader={true} isViewAll={true}/>
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

export default SearchResult;