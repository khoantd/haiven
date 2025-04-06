// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
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
  Steps,
  Divider,
  Spin,
  Alert,
  Tooltip,
  Collapse,
} from "antd";
import { 
  RiSendPlane2Line, 
  RiInformationLine, 
  RiLightbulbLine,
  RiArrowRightLine,
  RiFileCopyLine,
  RiDownloadLine
} from "react-icons/ri";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "../pages/_chat_header";
import { DynamicDataRenderer } from "../app/_dynamic_data_renderer";
import DocumentChoice from "../app/_document_choice";
import { getSortedUserDocuments, getSummaryForTheUserDocument } from "../app/_local_store";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Panel } = Collapse;

export default function BusinessStrategyPage() {
  const [strategyData, setStrategyData] = useState(null);
  const [citations, setCitations] = useState([]);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState("base");
  const [allDocuments, setAllDocuments] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();

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

  function combineAllDocuments(documents) {
    const userDocuments = getSortedUserDocuments();
    const userDocumentsForDropdown = userDocuments.map((document) => ({
      value: document.title,
      label: document.title,
      isUserDefined: true,
    }));
    
    // Always include the base option
    const baseOption = { value: "base", label: "No specific document", isUserDefined: false };
    
    if (documents !== undefined && documents.length > 0) {
      setAllDocuments([baseOption, ...documents, ...userDocumentsForDropdown]);
    } else {
      setAllDocuments([baseOption, ...userDocumentsForDropdown]);
    }
  }

  useEffect(() => {
    // Initialize with at least the base option
    combineAllDocuments([]);

    const handleStorageChange = () => {
      combineAllDocuments([]);
    };

    window.addEventListener("update-document", handleStorageChange);

    return () => {
      window.removeEventListener("update-document", handleStorageChange);
    };
  }, []);

  const handleStrategyGeneration = async (values) => {
    if (!values.companyName.trim() || !values.focusArea.trim()) {
      toast.warning("Please fill in all required fields");
      return;
    }

    setDisableInput(true);
    setStrategyData(null);
    setCitations([]);
    setError(null);
    startLoad();
    setCurrentStep(1);

    const uri = `/api/strategy`;

    try {
      // Prepare the request body with proper error handling
      const requestBody = {
        companyName: values.companyName,
        focusArea: values.focusArea,
        timeframe: values.timeframe || "medium_term", // Provide default if not selected
        additionalContext: values.additionalContext || "",
      };

      // Only add document information if a document is selected and it's not the base document
      if (selectedDocument && selectedDocument !== "base") {
        requestBody.document = selectedDocument;
      }

      const response = await fetch(uri, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.error) {
        setError(result.error);
        console.error("API Error:", result.error);
      } else if (result.data) {
        setStrategyData(result.data);
        setCurrentStep(2);
      } else {
        setError("No data received. Please try again.");
      }
    } catch (error) {
      console.error("Error:", error);
      setError(error.message || "Error generating strategy. Please try again.");
    } finally {
      setDisableInput(false);
      abortLoad();
    }
  };

  const createColumn = (columnConfig) => {
    return columnConfig.map((item, index) => (
      <Card
        key={index}
        title={
          <div className="card-title">
            <span className="card-title-text">{item.title}</span>
            <Tooltip title="Copy to clipboard">
              <Button 
                type="text" 
                icon={<RiFileCopyLine />} 
                onClick={() => {
                  navigator.clipboard.writeText(strategyData?.[item.property] || "");
                  toast.success("Copied to clipboard");
                }}
                className="copy-button"
              />
            </Tooltip>
          </div>
        }
        className="strategy-card"
        style={{ 
          marginBottom: "16px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
          borderRadius: "8px",
          overflow: "hidden"
        }}
      >
        <div className="card-content">
          {item.property === "implementation_plan" ? (
            <FormattedImplementationPlan data={strategyData?.[item.property]} />
          ) : (
            <FormattedTextContent data={strategyData?.[item.property]} />
          )}
        </div>
      </Card>
    ));
  };

  // Component to format implementation plan with proper styling
  const FormattedImplementationPlan = ({ data }) => {
    if (!data) return null;
    
    // Check if the data is a string that contains numbered items
    if (typeof data === 'string') {
      // Split by newlines and look for numbered items
      const lines = data.split('\n');
      const hasNumberedItems = lines.some(line => /^\d+\)/.test(line.trim()));
      
      if (hasNumberedItems) {
        return (
          <div className="implementation-plan">
            {lines.map((line, index) => {
              // Check if line starts with a number followed by a closing parenthesis
              const match = line.trim().match(/^(\d+)\)(.*)/);
              if (match) {
                const [, number, content] = match;
                return (
                  <div key={index} className="implementation-step">
                    <div className="step-number">{number}</div>
                    <div className="step-content">{content.trim()}</div>
                  </div>
                );
              }
              return <div key={index} className="text-paragraph">{line}</div>;
            })}
          </div>
        );
      }
    }
    
    // If not a numbered list, use the formatted text content
    return <FormattedTextContent data={data} />;
  };

  // Component to format text content with proper newline handling
  const FormattedTextContent = ({ data }) => {
    if (!data) return null;
    
    if (typeof data === 'string') {
      // Split by newlines and filter out empty lines
      const paragraphs = data.split('\n').filter(line => line.trim() !== '');
      
      if (paragraphs.length > 1) {
        return (
          <div className="formatted-text">
            {paragraphs.map((paragraph, index) => (
              <p key={index} className="text-paragraph">
                {paragraph}
              </p>
            ))}
          </div>
        );
      }
    }
    
    // Fallback to the default renderer for non-string data
    return <DynamicDataRenderer data={data} />;
  };

  const Citations = ({ citations }) => {
    if (!citations || citations.length === 0) return null;

    return (
      <Card 
        title={
          <div className="card-title">
            <span className="card-title-text">Sources</span>
          </div>
        }
        className="citations-card"
        style={{ 
          marginTop: "20px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
          borderRadius: "8px",
          overflow: "hidden"
        }}
      >
        <div className="citations-content">
          <ul className="citations-list">
            {citations.map((citation, index) => (
              <li key={index} className="citation-item">{citation}</li>
            ))}
          </ul>
        </div>
      </Card>
    );
  };

  const resetForm = () => {
    form.resetFields();
    setStrategyData(null);
    setCitations([]);
    setError(null);
    setCurrentStep(0);
  };

  const downloadStrategy = () => {
    if (!strategyData) return;
    
    try {
      const strategyText = Object.entries(strategyData)
        .map(([key, value]) => `## ${key.replace(/_/g, ' ').toUpperCase()}\n\n${value}\n\n`)
        .join('');
      
      const blob = new Blob([strategyText], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `business-strategy-${new Date().toISOString().split('T')[0]}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading strategy:", error);
      toast.error("Failed to download strategy. Please try again.");
    }
  };

  return (
    <ConfigProvider
      theme={{
        components: {
          Card: {
            headerBg: "var(--color-sapphire)",
            headerColor: "white",
            headerPadding: "12px 16px",
            bodyPadding: "16px",
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
          <Steps
            current={currentStep}
            items={[
              {
                title: 'Input Details',
                description: 'Provide company information',
              },
              {
                title: 'Generating',
                description: 'Creating strategy',
              },
              {
                title: 'Results',
                description: 'View strategy',
              },
            ]}
            style={{ marginBottom: "24px" }}
          />

          {!disableInput && currentStep === 0 && (
            <div className="strategy-form-container" style={{ marginBottom: "20px" }}>
              <Card 
                title={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <RiInformationLine style={{ marginRight: '8px' }} />
                    <span>Strategy Input</span>
                  </div>
                }
                className="strategy-form-card"
                style={{ 
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
                  borderRadius: "8px",
                  overflow: "hidden"
                }}
              >
                <Form
                  form={form}
                  onFinish={handleStrategyGeneration}
                  layout="vertical"
                  className="strategy-form"
                  initialValues={{
                    timeframe: "medium_term" // Set default timeframe
                  }}
                >
                  <Row gutter={16}>
                    <Col xs={24} md={12}>
                      <Form.Item
                        name="companyName"
                        label="Company Name"
                        rules={[{ required: true, message: "Please enter your company name" }]}
                      >
                        <Input placeholder="Enter your company name" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
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
                    </Col>
                  </Row>

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
                    tooltip="Add any specific details about your company, industry, or challenges"
                  >
                    <TextArea
                      rows={4}
                      placeholder="Add any specific context or requirements for the strategy"
                    />
                  </Form.Item>

                  <div className="user-input">
                    <label>
                      Select document
                      <HelpTooltip
                        text="Select a document from your knowledge pack that might have useful information for your business strategy. Haiven will try to find useful information in this document during strategy generation."
                        testid="document-selection-tooltip"
                      />
                    </label>
                    <Select
                      onChange={setSelectedDocument}
                      options={[
                        { value: "base", label: "No specific document" },
                        { value: "market_research", label: "Market Research" },
                        { value: "competitor_analysis", label: "Competitor Analysis" },
                        { value: "financial_forecast", label: "Financial Forecast" },
                        { value: "customer_feedback", label: "Customer Feedback" }
                      ]}
                      defaultValue="base"
                      data-testid="document-select"
                    />
                  </div>

                  <Divider />

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<RiSendPlane2Line />}
                      loading={loading}
                      size="large"
                      block
                    >
                      Generate Strategy
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            </div>
          )}

          {currentStep === 1 && (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Spin size="large" />
              <Paragraph style={{ marginTop: '20px', fontSize: '16px' }}>
                Generating your business strategy... This may take a moment.
              </Paragraph>
            </div>
          )}

          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              showIcon
              style={{ 
                marginBottom: "20px",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)"
              }}
              action={
                <Button size="small" onClick={resetForm}>
                  Try Again
                </Button>
              }
            />
          )}

          {strategyData && currentStep === 2 && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <Title level={4} style={{ margin: 0 }}>Your Business Strategy</Title>
                <Space>
                  <Button 
                    icon={<RiDownloadLine />} 
                    onClick={downloadStrategy}
                    type="primary"
                    style={{ borderRadius: "6px" }}
                  >
                    Download Strategy
                  </Button>
                  <Button 
                    onClick={resetForm}
                    style={{ borderRadius: "6px" }}
                  >
                    Generate New Strategy
                  </Button>
                </Space>
              </div>

              <Alert
                message="Strategy Generated Successfully"
                description="Below is your comprehensive business strategy. You can copy individual sections or download the entire strategy."
                type="success"
                showIcon
                style={{ 
                  marginBottom: "20px",
                  borderRadius: "8px",
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)"
                }}
              />

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

              <Citations citations={citations} />

              <Card 
                title={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <RiLightbulbLine style={{ marginRight: '8px' }} />
                    <span>Next Steps</span>
                  </div>
                }
                style={{ 
                  marginTop: '20px',
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
                  borderRadius: "8px",
                  overflow: "hidden"
                }}
              >
                <Paragraph style={{ fontSize: '16px', lineHeight: '1.6' }}>
                  Now that you have your business strategy, consider these next steps:
                </Paragraph>
                <ul style={{ fontSize: '16px', lineHeight: '1.6', paddingLeft: '20px' }}>
                  <li style={{ marginBottom: '8px' }}>Review the strategy with your team and stakeholders</li>
                  <li style={{ marginBottom: '8px' }}>Prioritize the implementation plan based on your resources</li>
                  <li style={{ marginBottom: '8px' }}>Set up regular check-ins to track progress against success metrics</li>
                  <li style={{ marginBottom: '8px' }}>Consider using our <a href="/chat?prompt=implementation">Implementation Planning</a> tool to create a detailed action plan</li>
                </ul>
              </Card>
            </>
          )}
        </div>
      </div>
      <style jsx global>{`
        .card-title {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
        }
        .card-title-text {
          font-weight: 600;
          font-size: 16px;
        }
        .copy-button {
          color: rgba(255, 255, 255, 0.8);
        }
        .copy-button:hover {
          color: white;
        }
        .card-content {
          font-size: 15px;
          line-height: 1.6;
        }
        .formatted-text {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .text-paragraph {
          margin: 0;
          padding: 0;
        }
        .citations-list {
          padding-left: 20px;
        }
        .citation-item {
          margin-bottom: 8px;
          font-size: 14px;
          line-height: 1.5;
        }
        .strategy-card .ant-card-head {
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        .strategy-card .ant-card-body {
          padding: 16px;
        }
        .citations-card .ant-card-head {
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        .citations-card .ant-card-body {
          padding: 16px;
        }
        .implementation-plan {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .implementation-step {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 8px 0;
          border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }
        .implementation-step:last-child {
          border-bottom: none;
        }
        .step-number {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          background-color: var(--color-sapphire);
          color: white;
          border-radius: 50%;
          font-weight: 600;
          flex-shrink: 0;
        }
        .step-content {
          flex: 1;
          padding-top: 2px;
        }
      `}</style>
    </ConfigProvider>
  );
} 