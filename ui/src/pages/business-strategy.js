// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import {
  Col,
  Row,
  Button,
  Input,
  Card,
  Typography,
  Form,
  Select,
  Space,
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

const { Title } = Typography;
const { TextArea } = Input;

export default function BusinessStrategyPage() {
  const [strategyData, setStrategyData] = useState(null);
  const [citations, setCitations] = useState([]);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);

  const strategyConfig = {
    title: "Business Strategy Brainstorming",
    key: "strategy",
    column1: [
      { title: "Market Analysis", property: "market_analysis" },
      { title: "Competitive Advantage", property: "competitive_advantage" }
    ],
    column2: [
      { title: "Growth Opportunities", property: "growth_opportunities" },
      { title: "Risk Assessment", property: "risk_assessment" },
      { title: "Resource Requirements", property: "resource_requirements" }
    ],
    column3: [
      { title: "Implementation Plan", property: "implementation_plan" },
      { title: "Success Metrics", property: "success_metrics" }
    ],
  };

  const title = (
    <div className="title">
      <h3>
        {strategyConfig.title}
        <HelpTooltip text="Generate business strategy insights" />
      </h3>
    </div>
  );

  const handleStrategyGeneration = async (values) => {
    if (!values.companyName.trim() || !values.focusArea.trim()) {
      toast.warning("Please fill in all required fields");
      return;
    }

    setDisableInput(true);
    setStrategyData(null);
    setCitations([]);
    setError(null);

    const uri = `/api/strategy`;

    try {
      const response = await fetch(uri, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          companyName: values.companyName,
          focusArea: values.focusArea,
          timeframe: values.timeframe,
          additionalContext: values.additionalContext
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.error) {
        setError(result.error);
        console.error("API Error:", result.error);
      } else if (result.data) {
        setStrategyData(result.data);
      } else {
        setError("No data received. Please try again.");
      }
    } catch (error) {
      console.error("Error:", error);
      setError("Error generating strategy. Please try again.");
    } finally {
      setDisableInput(false);
      abortLoad();
    }
  };

  const createColumn = (columnConfig) => {
    return columnConfig.map((item, index) => (
      <Card
        key={index}
        title={item.title}
        className="strategy-card"
        style={{ marginBottom: "16px" }}
      >
        <DynamicDataRenderer data={strategyData?.[item.property]} />
      </Card>
    ));
  };

  const Citations = ({ citations }) => {
    if (!citations || citations.length === 0) return null;

    return (
      <Card title="Sources" className="citations-card">
        <ul>
          {citations.map((citation, index) => (
            <li key={index}>{citation}</li>
          ))}
        </ul>
      </Card>
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
      <div className="strategy-page">
        <ChatHeader 
          models={{ chat: { name: "Strategy Generator" } }}
          titleComponent={title}
        />
        
        <div className="content-container" style={{ padding: "20px" }}>
          {!disableInput && (
            <div className="strategy-form-container" style={{ marginBottom: "20px" }}>
              <Form
                onFinish={handleStrategyGeneration}
                layout="vertical"
                className="strategy-form"
                style={{ maxWidth: "600px" }}
              >
                <Form.Item
                  name="companyName"
                  label="Company Name"
                  rules={[{ required: true, message: "Please enter your company name" }]}
                >
                  <Input placeholder="Enter your company name" />
                </Form.Item>

                <Form.Item
                  name="focusArea"
                  label="Strategy Focus Area"
                  rules={[{ required: true, message: "Please select a focus area" }]}
                >
                  <Select
                    placeholder="Select focus area"
                    options={[
                      { value: "market_expansion", label: "Market Expansion" },
                      { value: "product_development", label: "Product Development" },
                      { value: "digital_transformation", label: "Digital Transformation" },
                      { value: "cost_optimization", label: "Cost Optimization" },
                      { value: "sustainability", label: "Sustainability" }
                    ]}
                  />
                </Form.Item>

                <Form.Item
                  name="timeframe"
                  label="Strategic Timeframe"
                  rules={[{ required: true, message: "Please select a timeframe" }]}
                >
                  <Select
                    placeholder="Select timeframe"
                    options={[
                      { value: "short_term", label: "Short Term (1-2 years)" },
                      { value: "medium_term", label: "Medium Term (3-5 years)" },
                      { value: "long_term", label: "Long Term (5+ years)" }
                    ]}
                  />
                </Form.Item>

                <Form.Item
                  name="additionalContext"
                  label="Additional Context"
                >
                  <TextArea
                    rows={4}
                    placeholder="Add any specific context or requirements for the strategy"
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<RiSendPlane2Line />}
                    loading={loading}
                  >
                    Generate Strategy
                  </Button>
                </Form.Item>
              </Form>
            </div>
          )}

          {error && (
            <div className="error-message" style={{ color: "red", marginBottom: "20px" }}>
              {error}
            </div>
          )}

          {strategyData && (
            <Row gutter={[16, 16]}>
              <Col xs={24} md={8}>
                {createColumn(strategyConfig.column1)}
              </Col>
              <Col xs={24} md={8}>
                {createColumn(strategyConfig.column2)}
              </Col>
              <Col xs={24} md={8}>
                {createColumn(strategyConfig.column3)}
              </Col>
            </Row>
          )}

          <Citations citations={citations} />
        </div>
      </div>
    </ConfigProvider>
  );
} 