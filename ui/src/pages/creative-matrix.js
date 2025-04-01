// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { Input, Button, Select, Collapse, Form } from "antd";
import { UpOutlined } from "@ant-design/icons";
import {
  RiSendPlane2Line,
  RiStopCircleFill,
  RiAttachment2,
} from "react-icons/ri";
import { toast } from "react-toastify";
const { TextArea } = Input;
import { parse } from "best-effort-json-parser";
import { fetchSSE } from "../app/_fetch_sse";
import ChatHeader from "./_chat_header";
import useLoader from "../hooks/useLoader";

const CreativeMatrix = ({ models }) => {
  const [promptInput, setPromptInput] = useState("");
  const [rowsCSV, setRowsCSV] = useState("For Customers, For Employees");
  const [columnsCSV, setColumnsCSV] = useState(
    "For Tactical or Operational Tasks, For Creative or Strategic Tasks",
  );
  const [isPromptOptionsMenuExpanded, setPromptOptionsMenuExpanded] =
    useState(true);
  const [disableChatInput, setDisableChatInput] = useState(false);
  const [prompt, setPrompt] = useState(
    "Inspire me with generative AI use cases for Nike",
  );
  const [ideaQualifiers, setIdeaQualifiers] = useState("");
  const [numberOfIdeas, setNumberOfIdeas] = useState(3);
  const [rows, setRows] = useState(rowsCSV.split(",").map((v) => v.trim()));
  const [columns, setColumns] = useState(
    columnsCSV.split(",").map((v) => v.trim()),
  );
  const [isExpanded, setIsExpanded] = useState(true);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [matrix, setMatrix] = useState([]);
  const [templates, setTemplates] = useState([
    {
      name: "Template: GenAI Use Case Exploration Matrix",
      prompt: "Inspire me with generative AI use cases for Nike",
      rowsCSV: "For Customers, For Employees",
      columnsCSV:
        "For Tactical or Operational Tasks, For Creative or Strategic Tasks",
    },
    {
      name: "Template: GenAI Industry Examples",
      prompt: "How might we use generative AI?",
      rowsCSV:
        "To create new products, To streamline operations, To reach new customers",
      columnsCSV: "Financial Services, Healthcare, Retail",
    },
    {
      name: "Template: GenAI Value Chain Use Cases",
      prompt:
        "Inspire me with generative AI use cases across the wealth management value chain",
      rowsCSV: "For clients, For employees",
      columnsCSV:
        "Client acquisition, Financial planning, Portfolio construction, Investment execution, Performance monitoring, Reporting & Communication",
    },
    {
      name: "Template: Product Ideation Matrix",
      prompt:
        "How might make package holidays more attractive to our customers?",
      rowsCSV: "Inclusions, Partnerships, Discounts, Experiences",
      columnsCSV: "Families, Couples, Young Singles, Retirees",
    },
    {
      name: "Template: Blank Matrix",
      prompt: '"How might we" question',
      rowsCSV: "Row 1, Row 2, Row 3",
      columnsCSV: "Column 1, Column 2, Column 3",
    },
    {
      name: "Template: R&D Strategy & Value Chain Evolution",
      prompt: "Generate a comprehensive R&D strategy framework with aligned value chain stages and potential evolutions for a [startup/enterprise/industry]. Focus on key R&D priorities, capabilities, and innovation levers over time.",
      rowsCSV: "Business Goals, R&D Objectives, Key Capabilities, Technology Enablers, Talent & Organization, Strategic Partners",
      columnsCSV: "Discovery & Ideation, Proof of Concept, MVP Development, Productization, Scaling & Optimization, Long-term Innovation"
    },
    {
      name: "Template: R&D Strategy Across Innovation Lifecycle",
      prompt:
        "Inspire me with strategic R&D initiatives and priorities across the innovation lifecycle for a company or startup in any industry",
      rowsCSV: "Strategic Objectives, Core Technologies, Talent & Skills, Organizational Capabilities, Key Metrics, External Collaborations",
      columnsCSV:
        "Opportunity Scouting, Concept Development, Prototyping & Validation, Product Development, Go-to-Market Preparation, Continuous Improvement",
    },
    {
      name: "Template: R&D Value Chain Use Cases",
      prompt:
        "Inspire me with key activities, capabilities, and enablers across the R&D value chain for a company, startup, or enterprise in any industry",
      rowsCSV:
        "Scientific Research, Technology Development, Product Innovation, Process Engineering, Knowledge Management, Regulatory & IP Management",
      columnsCSV:
        "Idea Generation, Research Planning, Experimentation & Prototyping, Validation & Testing, Integration & Transfer, Commercialization Readiness",
    },
    {
      name: "Template: Business Model Canvas Inspiration",
      prompt:
        "Inspire me with innovative business model elements across the Business Model Canvas for any company, startup, or enterprise in any industry",
      rowsCSV: "Startup, Scale-up, Enterprise",
      columnsCSV:
        "Customer Segments, Value Propositions, Channels, Customer Relationships, Revenue Streams, Key Resources, Key Activities, Key Partnerships, Cost Structure",
    },
    {
      name: "Template: Strategic Planning Matrix",
      prompt:
        "Inspire me with strategic priorities, initiatives, and goals for building a comprehensive business strategic plan for any company, startup, or enterprise in any industry",
      rowsCSV: "Startup, Scale-up, Enterprise",
      columnsCSV:
        "Vision & Mission, Market Positioning, Customer Strategy, Product & Services, Go-to-Market Strategy, Operations & Delivery, Financial Model, People & Culture, Technology & Innovation"
    }
  ]);

  const onChangeRowsCSV = (e) => {
    setRowsCSV(e.target.value);
    setRows(e.target.value.split(",").map((v) => v.trim()));
  };

  const onChangeColumnsCSV = (e) => {
    setColumnsCSV(e.target.value);
    setColumns(e.target.value.split(",").map((v) => v.trim()));
  };

  const onChangePrompt = (e) => {
    setPrompt(e.target.value);
  };

  const onClickAdvancedPromptOptions = (e) => {
    setPromptOptionsMenuExpanded(!isPromptOptionsMenuExpanded);
  };

  const onChangeTemplate = (e) => {
    const template = templates.find((t) => t.name === e);
    setPrompt(template.prompt);
    setRowsCSV(template.rowsCSV);
    setColumnsCSV(template.columnsCSV);
    setRows(template.rowsCSV.split(",").map((v) => v.trim()));
    setColumns(template.columnsCSV.split(",").map((v) => v.trim()));
    setMatrix([]);
  };

  const handleSelectChange = (value) => {
    setNumberOfIdeas(value);
  };

  function onChangeIdeaQualifiers(e) {
    console.log(e);
    setIdeaQualifiers(e.join(", "));
  }

  const getMatrixCellValues = (rowIdx, columnIdx) => {
    const row = matrix[rowIdx] || [{ columns: [] }];
    const cell = (row && row.columns && row.columns[columnIdx]) || [
      { column: [], ideas: [] },
    ];
    let ret = cell || { ideas: [] };
    return ret.ideas || [];
  };

  const PromptHeader = () => {
    return (
      <div className="prompt-chat-header">
        <StopLoad />
      </div>
    );
  };

  const onSubmitPrompt = () => {
    setIsExpanded(false);
    setDisableChatInput(false);
    setPrompt("");
    setPromptOptionsMenuExpanded(false);

    const uri =
      "/api/creative-matrix?rows=" +
      encodeURIComponent(rowsCSV) +
      "&columns=" +
      encodeURIComponent(columnsCSV) +
      "&prompt=" +
      encodeURIComponent(prompt) +
      "&idea_qualifiers=" +
      encodeURIComponent(ideaQualifiers) +
      "&num_ideas=" +
      numberOfIdeas;

    let ms = "";
    let output = [];
    try {
      fetchSSE(
        uri,
        { method: "GET", signal: startLoad() },
        {
          json: true,
          onErrorHandle: () => {
            abortLoad();
          },
          onFinish: () => {
            if (ms == "") {
              toast.warning(
                "Model failed to respond rightly, please rewrite your message and try again",
              );
            }
            abortLoad();
          },
          onMessageHandle: (data) => {
            if (data.data) {
              ms += data.data;
              ms = ms.trim().replace(/^[^[]+/, "");
              if (ms.startsWith("[")) {
                try {
                  output = parse(ms || "[]");
                } catch (error) {
                  console.log("error", error);
                }
                if (Array.isArray(output)) {
                  setMatrix(output);
                } else {
                  abortLoad();
                  toast.warning(
                    "Model failed to respond rightly, please rewrite your message and try again",
                  );
                  console.log("response is not parseable into an array");
                }
              }
            }
          },
        },
      );
    } catch (error) {
      console.log("error", error);

      abortLoad();
    }
  };

  const title = (
    <div className="title">
      <h3>Creative Matrix</h3>
    </div>
  );

  const inputAreaRender = () => {
    const [form] = Form.useForm();

    const handleKeyDown = (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.submit();
      }
    };

    const items = [
      {
        key: "1",
        label: (
          <div className="advanced-prompting">
            Specify matrix parameters:
            <UpOutlined
              className="advanced-prompting-collapse-icon"
              rotate={isPromptOptionsMenuExpanded ? 180 : 0}
            />
          </div>
        ),
        children: advancedPromptingMenu,
        showArrow: false,
      },
    ];

    if (disableChatInput) {
      return null;
    }

    return (
      <div className="card-chat-input-container">
        <Collapse
          className="prompt-options-menu"
          items={items}
          defaultActiveKey={["1"]}
          ghost={isPromptOptionsMenuExpanded}
          activeKey={isPromptOptionsMenuExpanded ? "1" : ""}
          onChange={onClickAdvancedPromptOptions}
          collapsible="header"
        />
        <Form
          onFinish={async (value) => {
            const { question } = value;
            setPromptInput(question);
            await onSubmitPrompt();
            form.resetFields();
            setPrompt("");
          }}
          form={form}
          initialValues={{ question: "" }}
          className="chat-text-area-form"
        >
          <Form.Item
            name="question"
            rules={[{ required: true, message: "" }]}
            className="chat-text-area"
          >
            <Input.TextArea
              disabled={loading}
              placeholder="(Optional) Additional prompting about what you want to see in the matrix"
              autoSize={{ minRows: 1, maxRows: 4 }}
              onKeyDown={handleKeyDown}
              onChange={onChangePrompt}
            />
          </Form.Item>
          <Form.Item className="chat-text-area-submit">
            {loading ? (
              <Button
                type="secondary"
                icon={<RiStopCircleFill fontSize="large" />}
                onClick={() => abortLoad()}
              >
                STOP
              </Button>
            ) : (
              <Button
                htmlType="submit"
                icon={<RiSendPlane2Line fontSize="large" />}
                onClick={onSubmitPrompt}
                disabled={loading}
              >
                SEND
              </Button>
            )}
          </Form.Item>
        </Form>
      </div>
    );
  };

  const advancedPromptingMenu = (
    <div className="prompt-chat-creative-matrix">
      <div className="firstrow">
        <div className="creative-matrix-template">
          <label>Template</label>
          <Select
            defaultValue={templates[0].name}
            onChange={onChangeTemplate}
            options={templates.map((t) => ({
              value: t.name,
              label: t.name,
            }))}
          ></Select>
        </div>
        <div className="creative-matrix-ideas">
          <label>Each idea must be...</label>
          <Select
            mode="tags"
            placeholder="List of adjectives/qualifiers"
            onChange={onChangeIdeaQualifiers}
            disabled={loading}
            options={[
              { value: "utopian", label: "Utopian" },
              { value: "dystopian", label: "Dystopian" },
              {
                value: "inspired by science fiction",
                label: "Inspired by science fiction",
              },
              { value: "funny and bizarre", label: "Funny and bizarre" },
              {
                value: "written in the style of Shakespear",
                label: "Written in the style of Shakespear",
              },
            ]}
          />
        </div>
        <div className="creative-matrix-generate">
          <label>Generate</label>
          <Select
            defaultValue={"3"}
            onChange={handleSelectChange}
            disabled={loading}
            className="small"
            options={[
              { value: "1", label: "1 idea" },
              { value: "2", label: "2 ideas" },
              { value: "3", label: "3 ideas" },
              { value: "4", label: "4 ideas" },
              { value: "5", label: "5 ideas" },
            ]}
          ></Select>
        </div>
      </div>
      <div className="secondrow">
        <div className="creative-matrix-rows">
          <label>Rows</label>
          <TextArea
            placeholder="Comma-separated list of values"
            value={rowsCSV}
            onChange={onChangeRowsCSV}
            disabled={loading}
          />
        </div>
        <div className="creative-matrix-columns">
          <label>Columns</label>
          <TextArea
            placeholder="Comma-separated list of values"
            value={columnsCSV}
            onChange={onChangeColumnsCSV}
            disabled={loading}
          />
        </div>
      </div>
    </div>
  );

  const collapseItem = [
    {
      key: "1",
      children: advancedPromptingMenu,
    },
  ];

  return (
    <>
      <div id="canvas">
        <div className="prompt-chat-container">
          <div className="chat-container-wrapper">
            <ChatHeader models={models} titleComponent={title} />
            {!isExpanded ? <PromptHeader /> : () => {}}
            <div className="card-chat-container">
              <div className="matrix-container">
                <table className="matrix-table">
                  <thead>
                    <tr>
                      <th></th>
                      {columns.map((columnValue, index) => {
                        return <th>{columnValue}</th>;
                      })}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((rowValue, rowIndex) => {
                      return (
                        <tr style={{ height: 50 }}>
                          <td style={{ textAlign: "center", width: "10%" }}>
                            <b>{rowValue}</b>
                          </td>
                          {columns.map((columnValue, columnIndex) => {
                            return (
                              <td
                                style={{
                                  textAlign: "center",
                                  border: "1px solid #e1e1e1",
                                  width: 85 / columns.length + "%",
                                }}
                              >
                                <ul
                                  style={{ textAlign: "left", paddingLeft: 20 }}
                                >
                                  {getMatrixCellValues(
                                    rowIndex,
                                    columnIndex,
                                  ).map((idea) => {
                                    return (
                                      <li
                                        key={"" + rowIndex + "-" + columnIndex}
                                        style={{
                                          marginBottom: 10,
                                          cursor: "auto",
                                        }}
                                      >
                                        <b>{idea.title}:</b> {idea.description}
                                      </li>
                                    );
                                  })}
                                </ul>
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              {inputAreaRender()}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CreativeMatrix;
