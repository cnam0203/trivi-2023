import React, { useState } from "react";
import {
  Col,
  Dropdown,
  ButtonGroup,
  DropdownButton,
  Card,
} from "@themesberg/react-bootstrap";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

require("highcharts/modules/exporting")(Highcharts);
require("highcharts/modules/export-data.js")(Highcharts);

export default ({ rawChart }) => {
  var selections = ["line", "bar", "column", "area", "pie"];
  if (rawChart.isStack) {
    selections = selections.concat(["bar stack", "column stack"]);
  }

  const createChart = (
    title,
    chartData,
    chartType = "line",
    isStack = false
  ) => {
    var labels = [];
    var data = [];
    var xCategories = [];
    var groupCategories = [];

    if (chartData.length) {
      var rawData = chartData.map((row) =>
        Object.keys(row).map((key) => row[key])
      );
      labels = Object.keys(chartData[0]);
      xCategories = [...new Set(rawData.map((data) => data[0]))].sort();

      if (labels.length === 2) {
        data = rawData;
      } else if (labels.length === 3) {
        isStack = true;
        groupCategories = [...new Set(rawData.map((data) => data[1]))].sort();
        data = groupCategories.map((groupCategory) => {
          let arrValues = xCategories.map((xCategory) => {
            var newArray = rawData.filter(function (data) {
              return data[0] === xCategory && data[1] === groupCategory;
            });

            if (newArray.length) return newArray[0][2];
            else return 0;
          });

          return {
            name: groupCategory,
            data: arrValues,
          };
        });
      }
    } else {
      return {
        title: {
          text: title ? title : "",
          margin: 20,
          style: {
            fontSize: "1.25rem",
            color: "#262B40",
          },
        },
      };
    }

    return {
      title: {
        text: title ? title : "",
        margin: 20,
        style: {
          fontSize: "1.25rem",
          color: "#262B40",
        },
      },
      chart: {
        type: chartType ? chartType : "line",
        style: {
          fontFamily: "Nunito Sans",
        },
      },
      series:
        labels.length == 2
          ? [
              {
                name: "",
                data: data,
                colorByPoint: true,
              },
            ]
          : data,
      exporting: {
        enabled: true,
        showTable: false,
      },
      xAxis: {
        type: "category",
        categories: xCategories,
      },
      yAxis: {
        title: {
          text: "Total number",
        },
      },
      legend: {
        enabled: labels.length === 3 ? true : false,
      },
      plotOptions: {
        series: {
          borderWidth: 0,
          dataLabels: {
            enabled: true,
          },
          showInLegend: true,
          stacking: isStack,
        },
        pie: {
          allowPointSelect: true,
          cursor: "pointer",
          dataLabels: {
            enabled: true,
            format: "<b>{point.name}</b>: {point.percentage:.1f} %",
          },
        },
      },
      options: {
        charts: {
          style: {
            fontFamily: "Nunito Sans",
          },
        },
      },
    };
  };

  const [chart, setChart] = useState(
    createChart(rawChart.title, rawChart.data, rawChart.type, rawChart.isStack)
  );

  const handleSelect = (e) => {
    const newChartType = e.split(" ")[0];
    const isStackChart = e.includes("stack") ? true : false;
    const newChart = createChart(
      rawChart.title,
      rawChart.data,
      newChartType,
      isStackChart
    );
    setChart(newChart);
  };

  return (
    <Col xs={12} xl={12} sm={12} className="mb-4">
      <Card
        border="light"
        className="shadow-sm p-3"
        style={{ overflow: "hidden" }}
      >
        {rawChart["isChange"] ? (
          <DropdownButton
            as={ButtonGroup}
            title="Chart type"
            onSelect={handleSelect}
            className="col-3"
          >
            {selections.map((type, index) => (
              <Dropdown.Item key={index} eventKey={type}>
                {type}
              </Dropdown.Item>
            ))}
          </DropdownButton>
        ) : (
          <></>
        )}
        <HighchartsReact highcharts={Highcharts} options={chart} />
      </Card>
    </Col>
  );
};
