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
  const [isViewDetail, setIsViewDetail] = useState(false);
  const [items, setItems] = useState([]);
  const [searchItems, setSearchItems] = useState([]);
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
    fetchRequest(`data/get-matching-template/${itemType}`, 'GET')
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

  const handleViewDetail = (row) => {
    const id = row["id"];
    const url = `/data-management/detail-template/${itemType}?templ_id=${id}`;
    history.push(url);
  };

  const handleNewItem = () => {
    const url = `/data-management/new-template/${itemType}`;
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
        <Row className="d-flex flex-wrap flex-md-nowrap align-items-center py-4">
          <Col className="d-block mb-4 mb-md-0">
            <h1 className="h2">Templates - {itemType}</h1>
          </Col>
        </Row>
        <Row>
          <Col xs={9} className="mb-4">
            {isViewDetail ? (
              <Button
                variant="primary"
                className="m-1"
                onClick={() => handleNewItem()}
              >
                New template
              </Button>
            ) : (
              <></>
            )}
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
        {columns.length > 0 ? (
          <ProcessTables
            columns={columns}
            data={searchItems}
            isViewDetail={isViewDetail}
            handleViewDetail={handleViewDetail}
          />
        ) : (
          <></>
        )}
      </Container>
    </article>
  );
};
