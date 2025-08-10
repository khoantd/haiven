// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import {
  Col,
  Row,
  Button,
  Input,
  Card,
  List,
  Typography,
  Form,
  ConfigProvider,
} from "antd";
import { RiSendPlane2Line } from "react-icons/ri";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "../pages/_chat_header";
import { DynamicDataRenderer } from "../app/_dynamic_data_renderer";
import LLMTokenUsage from "../app/_llm_token_usage";
import { formattedUsage } from "../app/utils/tokenUtils";
import { aggregateTokenUsage } from "../app/utils/_aggregate_token_usage";
import { filterSSEEvents } from "../app/utils/_sse_event_filter";

const { Title } = Typography;

export default function CompanyCanvas({
  researchConfig,
  featureToggleConfig = {},
}) {
  const [companyName, setCompanyName] = useState("");
  const [companyData, setCompanyData] = useState(null);
  const [citations, setCitations] = useState([]);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);
  const [tokenUsage, setTokenUsage] = useState({
    input_tokens: 0,
    output_tokens: 0,
  });

  const handleSearch = async (input) => {
    if (!input.trim()) {
      toast.error("Please enter a company name");
      return;
    }

    const signal = startLoad();

    setCompanyName(input);
    setDisableInput(true);
    setCompanyData(null);
    setCitations([]);
    setError(null);
    setTokenUsage({ input_tokens: 0, output_tokens: 0 });

    const uri = `/api/research`;

    let jsonResponse = "";

    fetchSSE(
      uri,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ userinput: input, config: researchConfig.key }),
        signal: signal,
      },
      {
        json: true,
        onErrorHandle: (err) => {
          setDisableInput(false);
          setError("Error fetching company data. Please try again.");
          console.error("Error:", err);
          abortLoad();
        },
        onFinish: () => {
          setDisableInput(false);
          if (jsonResponse === "") {
            setError("No data received. Please try again.");
          }
          abortLoad();
        },
        onMessageHandle: (data) => {
          try {
            // Handle token usage events first
            if (typeof data === "string") {
              const { text, events } = filterSSEEvents(data);
              events.forEach((event) => {
                if (event.type === "token_usage") {
                  const usage = formattedUsage(event.data);
                  setTokenUsage((prev) => aggregateTokenUsage(prev, usage));
                }
              });
              // Continue with regular data processing only if there's text content
              if (text) {
                data = { data: text };
              } else {
                return; // No text content, just token usage events
              }
            } else if (
              typeof data === "object" &&
              data.type === "token_usage"
            ) {
              const usage = formattedUsage(data.data);
              setTokenUsage((prev) => aggregateTokenUsage(prev, usage));
              return; // Exit early for token usage events
            }

            // Only process data.data if it exists
            if (data.data) {
              if (data.data.startsWith("```")) {
                data.data = data.data.substring(3);
              }
              if (data.data.startsWith("json")) {
                data.data = data.data.substring(4);
              }

              jsonResponse += data.data;
              jsonResponse = jsonResponse.trim();

              // Try to parse the JSON even if it's incomplete
              try {
                const parsedData = parse(jsonResponse);
                if (parsedData && typeof parsedData === "object") {
                  setCompanyData(parsedData);
                } else {
                  // not JSON
                  console.log("response is not parseable JSON");
                  setDisableInput(false);
                  toast.warning(
                    "Model failed to respond in a structured way, this sometimes happens. You can try again.",
                  );
                  abortLoad();
                }
              } catch (error) {
                // This is expected for partial JSON, no need to log every attempt
              }
            } else if (data.metadata) {
              // Safely handle citations if they exist in metadata
              if (data.metadata.citations) {
                setCitations(data.metadata.citations);
              }
            }
          } catch (error) {
            console.log(
              "Error processing message:",
              error,
              "data received:",
              data,
            );
          }
        },
      },
    );
  };

  const title = researchConfig && (
    <div className="title">
      <h3>
        {researchConfig.title}
        <HelpTooltip text={researchConfig.description} />
      </h3>
      <LLMTokenUsage
        tokenUsage={tokenUsage}
        featureToggleConfig={featureToggleConfig}
      />
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

    if (disableInput) {
      return null;
    }

    return (
      <div className="search-container" style={{ marginBottom: "20px" }}>
        <Form
          onFinish={async (value) => {
            await handleSearch(value.companyName);
            form.resetFields();
          }}
          form={form}
          initialValues={{ companyName: "" }}
          className="company-search-form"
          style={{ display: "flex", maxWidth: "450px" }}
        >
          <Form.Item
            name="companyName"
            rules={[{ required: true, message: "Please enter a company name" }]}
            style={{ marginBottom: 0, marginRight: "10px", flex: 1 }}
          >
            <Input
              placeholder="Enter company name"
              disabled={loading}
              onKeyDown={handleKeyDown}
              style={{ width: "100%", maxWidth: "300px" }}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            {!loading && (
              <Button htmlType="submit" icon={<RiSendPlane2Line />}>
                Research
              </Button>
            )}
          </Form.Item>
        </Form>
      </div>
    );
  };

  const createColumn = (columnConfig) => {
    return (
      <Col xs={24} lg={8} className="results-column">
        {columnConfig.map((item, index) => (
          <Card
            key={index}
            title={item.title}
            loading={loading && !companyData[item.property]}
          >
            {Array.isArray(companyData[item.property]) ? (
              companyData[item.property].map((listItem, listIndex) => (
                <Card
                  key={index + "-" + listIndex}
                  size="small"
                  className="inner-result"
                >
                  <DynamicDataRenderer data={listItem} />
                </Card>
              ))
            ) : (
              <DynamicDataRenderer data={companyData[item.property]} />
            )}
          </Card>
        ))}
      </Col>
    );
  };

  const Citations = ({ citations }) => {
    if (!citations || !Array.isArray(citations) || citations.length === 0) {
      return null;
    }

    return (
      <div className="citations-section">
        <Typography.Title level={5} style={{ marginTop: "0" }}>
          Sources
        </Typography.Title>
        <List
          size="small"
          itemLayout="horizontal"
          dataSource={citations}
          style={{ fontSize: "12px" }}
          renderItem={(citation) => {
            // Handle both string URLs and object citations
            const url = typeof citation === "string" ? citation : citation.url;

            if (!url) return null;

            return (
              <List.Item style={{ padding: "2px 0" }}>
                <ul
                  style={{
                    listStyleType: "disc",
                    margin: 0,
                    paddingLeft: "20px",
                  }}
                >
                  <li>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontSize: "12px", lineHeight: "1.2" }}
                    >
                      {url}
                    </a>
                  </li>
                </ul>
              </List.Item>
            );
          }}
        />
      </div>
    );
  };

  return (
    <ConfigProvider
      theme={{
        components: {
          Card: {
            headerBg: "var(--color-sapphire)",
          },
        },
      }}
    >
      <ChatHeader
        models={{ chat: { name: "Perplexity AI" } }}
        titleComponent={title}
      />
      <div className="company-research dashboard">
        {inputAreaRender()}

        {error && (
          <div
            className="error-container"
            style={{ color: "red", margin: "20px 0" }}
          >
            {error}
          </div>
        )}

        <StopLoad />

        {companyData && (
          <div className="research-results">
            <div className="research-results-section">
              <div className="title-container">
                <Title level={3}>
                  {companyData.business_brief?.company_name || companyName}
                </Title>
              </div>

              <Row gutter={[12, 12]} className="results-row">
                {createColumn(researchConfig.column1)}
                {createColumn(researchConfig.column2)}
                {createColumn(researchConfig.column3)}
              </Row>
            </div>

            <Row gutter={[12, 12]} className="results-row citations-container">
              <Citations citations={citations} />
            </Row>
          </div>
        )}
      </div>
    </ConfigProvider>
  );
}
