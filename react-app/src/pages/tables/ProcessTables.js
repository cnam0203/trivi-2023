import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleDown, faTrash } from "@fortawesome/free-solid-svg-icons";
import {
  Col,
  Row,
  Table,
  Card,
  Button,
  Pagination,
  ButtonGroup,
  Dropdown,
} from "@themesberg/react-bootstrap";
import { useTable, useSortBy, usePagination } from "react-table";

export default ({ columns, 
  data, 
  isViewDetail = false, 
  handleViewDetail, 
  isClick = false, 
  clickTitle, 
  handleClick, 
  isShowPagnition = true, 
  isDeleteColumn = false,
  handleDelete}) => {
  const selections = [10, 20, 50, 100];
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    canPreviousPage,
    canNextPage,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data,
      initialState: { pageIndex: 0, pageSize: 20 },
    },
    useSortBy,
    usePagination
  );

  const indexItems = [];
  const totalPages = Math.ceil(data.length / pageSize);
  const limitPage = 9;

  let arrayItems = [];
  let min = 0;
  let max = 0;
  let isPrev = false;
  let isNext = false;

  if (limitPage >= pageIndex + 1) {
    if (limitPage >= totalPages) {
      min = 1;
      max = totalPages;
    } else {
      min = 1;
      max = limitPage;
      isNext = true;
    }
  } else if (totalPages - limitPage + 1 <= pageIndex + 1) {
    if (totalPages - limitPage <= 0) {
      min = 1;
      max = totalPages;
    } else {
      min = totalPages - limitPage + 1;
      max = totalPages;
      isPrev = true;
    } 
  } else {
    isPrev = true;
    min = pageIndex - Math.floor(limitPage/2);
    max = pageIndex + Math.ceil(limitPage/2);
    isNext = true;
  }
  
  for (let i = min; i <= max; i++) {
    arrayItems.push(i)
  }

  if (isPrev) {
    indexItems.push(
    <Pagination.Ellipsis
      key={min-1}
      onClick={() => gotoPage(min-2)}
    />)
  } 

  arrayItems.map(item => {
       indexItems.push(
        <Pagination.Item
          active={pageIndex == item-1}
          key={item}
          onClick={() => gotoPage(item-1)}
        >
          {item}
        </Pagination.Item>
      )
  })

  if (isNext) {
    indexItems.push(
    <Pagination.Ellipsis
      key={max+1}
      onClick={() => gotoPage(max)}
    />)
  } 
  // for (let number = 0; number < totalPages; number++) {
  //   const isItemActive = pageIndex === number;

  //   indexItems.push(
  //     <Pagination.Item
  //       active={isItemActive}
  //       key={number}
  //       onClick={() => gotoPage(number)}
  //     >
  //       {number + 1}
  //     </Pagination.Item>
  //   );

  const onClickRow = (index, row) => {
    if (index === 0) {
      if (isViewDetail) handleViewDetail(row);
    }
  };

  return (
    <>
      <Row>
        <Col xs={12} className="mb-4">
          <Card>
            <Card.Body>
              <Table {...getTableProps()} striped bordered hover responsive>
                <thead className="thead-light">
                  {headerGroups.map((headerGroup) => (
                    <tr {...headerGroup.getHeaderGroupProps()}>
                      {headerGroup.headers.map((column) => (
                        <th
                          {...column.getHeaderProps(
                            column.getSortByToggleProps()
                          )}
                          className="border-0"
                        >
                          {column.render("Header")}
                          <span>
                            {column.isSorted
                              ? column.isSortedDesc
                                ? " 🔽"
                                : " 🔼"
                              : ""}
                          </span>
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody {...getTableBodyProps()}>
                  {page.map((row, i) => {
                    prepareRow(row);
                    return (
                      <tr {...row.getRowProps()}>
                        {row.cells.map((cell, index) => {
                          return (
                            <td
                              className="border-0 fw-bold"
                              {...cell.getCellProps()}
                              style={{
                                cursor: index === 0 ? "pointer" : "mouse",
                              }}
                              onClick={() => onClickRow(index, row.values)}
                            >
                              {cell.render("Cell")}
                            </td>
                          );
                        })}
                        {isClick ? 
                          <td
                            className="border-0 fw-bold"
                          >
                            <Button
                              variant="primary"
                              onClick={() => handleClick(row.cells[0].value)}
                            >{clickTitle}</Button>
                          </td> : <></>
                        }
                        {isDeleteColumn ? 
                          <td
                            className="border-0 fw-bold"
                          >
                            <Button
                              variant="danger"
                              onClick={() => handleDelete(row.cells[0].value)}
                            ><FontAwesomeIcon icon={faTrash} size={'xs'}/></Button>
                          </td> : <></>
                        }
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      {
        isShowPagnition ? <Row>
        <Col xs={3} className="mb-4">
          <Dropdown
            as={ButtonGroup}
            onSelect={(e) => setPageSize(Number(e))}
            className="m-1"
          >
            <Button variant="light">{`Show ${pageSize} entries`}</Button>
            <Dropdown.Toggle split variant="light">
              <FontAwesomeIcon icon={faAngleDown} className="dropdown-arrow" />
            </Dropdown.Toggle>
            <Dropdown.Menu>
              {selections.map((type, index) => (
                <Dropdown.Item key={index} eventKey={type}>
                  {type}
                </Dropdown.Item>
              ))}
            </Dropdown.Menu>
          </Dropdown>
        </Col>
        <Col xs={9} className="mb-4">
          <Pagination size="md" className="mt-3">
            <Pagination.Prev
              onClick={() => previousPage()}
              disabled={!canPreviousPage}
            >
              {"Previous"}
            </Pagination.Prev>
            {indexItems}
            <Pagination.Next onClick={() => nextPage()} disabled={!canNextPage}>
              {"Next"}
            </Pagination.Next>
          </Pagination>
        </Col>
      </Row> : <></>
      }
    </>
  );
};
