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
  Tabs,
  Collapse,
} from "antd";
import { 
  RiSendPlane2Line, 
  RiInformationLine, 
  RiLightbulbLine,
  RiFileCopyLine,
  RiDownloadLine,
  RiBarChartBoxLine,
  RiLineChartLine,
  RiPieChartLine,
  RiTableLine
} from "react-icons/ri";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "../pages/_chat_header";
import { DynamicDataRenderer } from "../app/_dynamic_data_renderer";
import { getDocuments } from "../app/_boba_api";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Panel } = Collapse;
const { TabPane } = Tabs;

export default function StrategyEvaluationPage() {
  const [evaluationData, setEvaluationData] = useState(null);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState("base");
  const [documents, setDocuments] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState("swot");

  useEffect(() => {
    // Load documents from the API
    getDocuments((docs) => {
      const baseOption = { value: "base", label: "No specific document" };
      setDocuments([baseOption, ...docs]);
    });
  }, []);

  const handleStrategyEvaluation = async (values) => {
    if (!values.companyName.trim()) {
      toast.warning("Please enter the company name");
      return;
    }

    setDisableInput(true);
    setEvaluationData(null);
    setError(null);
    startLoad();
    setCurrentStep(1);

    const uri = `/api/strategy/evaluate`;

    try {
      const requestBody = {
        companyName: values.companyName,
        frameworks: values.frameworks || [
          "swot", 
          "value_chain", 
          "five_forces", 
          "comparative_advantage",
          "pestel",
          "ansoff",
          "bcg",
          "value_proposition"
        ],
        additionalContext: values.additionalContext || "",
      };

      // Add strategy if provided
      if (values.strategy && values.strategy.trim()) {
        requestBody.strategy = values.strategy;
      }

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
        setEvaluationData(result.data);
        setCurrentStep(2);
      } else {
        setError("No data received. Please try again.");
      }
    } catch (error) {
      console.error("Error:", error);
      setError(error.message || "Error evaluating strategy. Please try again.");
    } finally {
      setDisableInput(false);
      abortLoad();
    }
  };

  const resetForm = () => {
    form.resetFields();
    setEvaluationData(null);
    setError(null);
    setCurrentStep(0);
  };

  const downloadEvaluation = () => {
    if (!evaluationData) return;
    
    try {
      const evaluationText = Object.entries(evaluationData)
        .map(([key, value]) => `## ${key.replace(/_/g, ' ').toUpperCase()}\n\n${value}\n\n`)
        .join('');
      
      const blob = new Blob([evaluationText], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `strategy-evaluation-${new Date().toISOString().split('T')[0]}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading evaluation:", error);
      toast.error("Failed to download evaluation. Please try again.");
    }
  };

  const renderFrameworkContent = (framework) => {
    if (!evaluationData || !evaluationData[framework]) return null;

    const data = evaluationData[framework];
    switch (framework) {
      case "swot":
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="Strengths" className="analysis-card">
                <DynamicDataRenderer data={data.strengths} />
              </Card>
              <Card title="Weaknesses" className="analysis-card">
                <DynamicDataRenderer data={data.weaknesses} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="Opportunities" className="analysis-card">
                <DynamicDataRenderer data={data.opportunities} />
              </Card>
              <Card title="Threats" className="analysis-card">
                <DynamicDataRenderer data={data.threats} />
              </Card>
            </Col>
          </Row>
        );
      case "pestel":
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={8}>
              <Card title="Political" className="analysis-card">
                <DynamicDataRenderer data={data.political} />
              </Card>
              <Card title="Economic" className="analysis-card">
                <DynamicDataRenderer data={data.economic} />
              </Card>
            </Col>
            <Col xs={24} md={8}>
              <Card title="Social" className="analysis-card">
                <DynamicDataRenderer data={data.social} />
              </Card>
              <Card title="Technological" className="analysis-card">
                <DynamicDataRenderer data={data.technological} />
              </Card>
            </Col>
            <Col xs={24} md={8}>
              <Card title="Environmental" className="analysis-card">
                <DynamicDataRenderer data={data.environmental} />
              </Card>
              <Card title="Legal" className="analysis-card">
                <DynamicDataRenderer data={data.legal} />
              </Card>
            </Col>
          </Row>
        );
      case "ansoff":
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="Market Penetration" className="analysis-card">
                <DynamicDataRenderer data={data.market_penetration} />
              </Card>
              <Card title="Market Development" className="analysis-card">
                <DynamicDataRenderer data={data.market_development} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="Product Development" className="analysis-card">
                <DynamicDataRenderer data={data.product_development} />
              </Card>
              <Card title="Diversification" className="analysis-card">
                <DynamicDataRenderer data={data.diversification} />
              </Card>
            </Col>
          </Row>
        );
      case "bcg":
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="Stars" className="analysis-card">
                <DynamicDataRenderer data={data.stars} />
              </Card>
              <Card title="Question Marks" className="analysis-card">
                <DynamicDataRenderer data={data.question_marks} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="Cash Cows" className="analysis-card">
                <DynamicDataRenderer data={data.cash_cows} />
              </Card>
              <Card title="Dogs" className="analysis-card">
                <DynamicDataRenderer data={data.dogs} />
              </Card>
            </Col>
          </Row>
        );
      case "value_proposition":
        return (
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="Customer Profile" className="analysis-card">
                <DynamicDataRenderer data={data.customer_profile} />
              </Card>
              <Card title="Customer Jobs" className="analysis-card">
                <DynamicDataRenderer data={data.customer_jobs} />
              </Card>
              <Card title="Customer Pains" className="analysis-card">
                <DynamicDataRenderer data={data.customer_pains} />
              </Card>
              <Card title="Customer Gains" className="analysis-card">
                <DynamicDataRenderer data={data.customer_gains} />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="Value Proposition" className="analysis-card">
                <DynamicDataRenderer data={data.value_proposition} />
              </Card>
              <Card title="Products & Services" className="analysis-card">
                <DynamicDataRenderer data={data.products_services} />
              </Card>
              <Card title="Pain Relievers" className="analysis-card">
                <DynamicDataRenderer data={data.pain_relievers} />
              </Card>
              <Card title="Gain Creators" className="analysis-card">
                <DynamicDataRenderer data={data.gain_creators} />
              </Card>
            </Col>
          </Row>
        );
      case "value_chain":
        return (
          <Card className="analysis-card">
            <DynamicDataRenderer data={data} />
          </Card>
        );
      case "five_forces":
        return (
          <Card className="analysis-card">
            <DynamicDataRenderer data={data} />
          </Card>
        );
      case "comparative_advantage":
        return (
          <Card className="analysis-card">
            <DynamicDataRenderer data={data} />
          </Card>
        );
      default:
        return null;
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
      <div className="strategy-evaluation-page">
        <ChatHeader 
          models={{ chat: { name: "Strategy Evaluator" } }}
          titleComponent={
            <div className="title">
              <h3>
                Business Strategy Evaluation
                <HelpTooltip text="Evaluate business strategies using multiple frameworks" />
              </h3>
            </div>
          }
        />
        
        <div className="content-container" style={{ padding: "20px" }}>
          <Steps
            current={currentStep}
            items={[
              {
                title: 'Input Details',
                description: 'Provide company and strategy information',
              },
              {
                title: 'Evaluating',
                description: 'Analyzing strategy',
              },
              {
                title: 'Results',
                description: 'View evaluation',
              },
            ]}
            style={{ marginBottom: "24px" }}
          />

          {!disableInput && currentStep === 0 && (
            <div className="evaluation-form-container" style={{ marginBottom: "20px" }}>
              <Card 
                title={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <RiInformationLine style={{ marginRight: '8px' }} />
                    <span>Strategy Input</span>
                  </div>
                }
                className="evaluation-form-card"
                style={{ 
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
                  borderRadius: "8px",
                  overflow: "hidden"
                }}
              >
                <Form
                  form={form}
                  onFinish={handleStrategyEvaluation}
                  layout="vertical"
                  className="evaluation-form"
                >
                  <Row gutter={16}>
                    <Col xs={24} md={12}>
                      <Form.Item
                        name="companyName"
                        label="Company Name"
                        rules={[{ required: true, message: "Please enter the company name" }]}
                      >
                        <Input placeholder="Enter company name" />
                      </Form.Item>
                    </Col>
                    <Col xs={24} md={12}>
                      <Form.Item
                        name="frameworks"
                        label="Analysis Frameworks"
                        rules={[{ required: true, message: "Please select at least one framework" }]}
                      >
                        <Select
                          mode="multiple"
                          placeholder="Select frameworks"
                          options={[
                            { value: "swot", label: "SWOT/TOWS Analysis" },
                            { value: "pestel", label: "PESTEL Analysis" },
                            { value: "ansoff", label: "Ansoff Matrix" },
                            { value: "bcg", label: "BCG Matrix" },
                            { value: "value_proposition", label: "Value Proposition Canvas" },
                            { value: "value_chain", label: "Value Chain Analysis" },
                            { value: "five_forces", label: "Five Forces Analysis" },
                            { value: "comparative_advantage", label: "Comparative Advantage" }
                          ]}
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="strategy"
                    label="Business Strategy"
                    tooltip="Optional: Enter the business strategy to evaluate. If not provided, the evaluation will focus on the company's current position."
                  >
                    <TextArea
                      rows={6}
                      placeholder="Enter the business strategy to evaluate (optional)"
                    />
                  </Form.Item>

                  <Form.Item
                    name="additionalContext"
                    label="Additional Context"
                    tooltip="Add any specific details about the company, industry, or challenges"
                  >
                    <TextArea
                      rows={4}
                      placeholder="Add any specific context or requirements for the evaluation"
                    />
                  </Form.Item>

                  <div className="user-input">
                    <label>
                      Select document
                      <HelpTooltip
                        text="Select a document from your knowledge pack that might have useful information for the strategy evaluation."
                        testid="document-selection-tooltip"
                      />
                    </label>
                    <Select
                      onChange={setSelectedDocument}
                      options={documents}
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
                      Evaluate Strategy
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
                Evaluating your business strategy... This may take a moment.
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

          {evaluationData && currentStep === 2 && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <Title level={4} style={{ margin: 0 }}>Strategy Evaluation Results</Title>
                <Space>
                  <Button 
                    icon={<RiDownloadLine />} 
                    onClick={downloadEvaluation}
                    type="primary"
                    style={{ borderRadius: "6px" }}
                  >
                    Download Evaluation
                  </Button>
                  <Button 
                    onClick={resetForm}
                    style={{ borderRadius: "6px" }}
                  >
                    New Evaluation
                  </Button>
                </Space>
              </div>

              <Alert
                message="Evaluation Complete"
                description="Below is your comprehensive strategy evaluation using the selected frameworks."
                type="success"
                showIcon
                style={{ 
                  marginBottom: "20px",
                  borderRadius: "8px",
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)"
                }}
              />

              <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                items={[
                  {
                    key: "swot",
                    label: (
                      <span>
                        <RiBarChartBoxLine style={{ marginRight: '8px' }} />
                        SWOT/TOWS
                      </span>
                    ),
                    children: renderFrameworkContent("swot")
                  },
                  {
                    key: "pestel",
                    label: (
                      <span>
                        <RiBarChartBoxLine style={{ marginRight: '8px' }} />
                        PESTEL
                      </span>
                    ),
                    children: renderFrameworkContent("pestel")
                  },
                  {
                    key: "ansoff",
                    label: (
                      <span>
                        <RiBarChartBoxLine style={{ marginRight: '8px' }} />
                        Ansoff
                      </span>
                    ),
                    children: renderFrameworkContent("ansoff")
                  },
                  {
                    key: "bcg",
                    label: (
                      <span>
                        <RiBarChartBoxLine style={{ marginRight: '8px' }} />
                        BCG
                      </span>
                    ),
                    children: renderFrameworkContent("bcg")
                  },
                  {
                    key: "value_proposition",
                    label: (
                      <span>
                        <RiBarChartBoxLine style={{ marginRight: '8px' }} />
                        Value Proposition
                      </span>
                    ),
                    children: renderFrameworkContent("value_proposition")
                  },
                  {
                    key: "value_chain",
                    label: (
                      <span>
                        <RiLineChartLine style={{ marginRight: '8px' }} />
                        Value Chain
                      </span>
                    ),
                    children: renderFrameworkContent("value_chain")
                  },
                  {
                    key: "five_forces",
                    label: (
                      <span>
                        <RiPieChartLine style={{ marginRight: '8px' }} />
                        Five Forces
                      </span>
                    ),
                    children: renderFrameworkContent("five_forces")
                  },
                  {
                    key: "comparative_advantage",
                    label: (
                      <span>
                        <RiTableLine style={{ marginRight: '8px' }} />
                        Comparative Advantage
                      </span>
                    ),
                    children: renderFrameworkContent("comparative_advantage")
                  }
                ]}
              />

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
                  Now that you have your strategy evaluation, consider these next steps:
                </Paragraph>
                <ul style={{ fontSize: '16px', lineHeight: '1.6', paddingLeft: '20px' }}>
                  <li style={{ marginBottom: '8px' }}>Review the evaluation with your team and stakeholders</li>
                  <li style={{ marginBottom: '8px' }}>Identify key areas for improvement based on the analysis</li>
                  <li style={{ marginBottom: '8px' }}>Use the insights to refine your business strategy</li>
                  <li style={{ marginBottom: '8px' }}>Consider using our <a href="/business-strategy">Business Strategy</a> tool to develop an improved strategy</li>
                </ul>
              </Card>
            </>
          )}
        </div>
      </div>
      <style jsx global>{`
        .analysis-card {
          margin-bottom: 16px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          border-radius: 8px;
          overflow: hidden;
        }
        .analysis-card .ant-card-head {
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        .analysis-card .ant-card-body {
          padding: 16px;
        }
        .ant-tabs-tab {
          display: flex;
          align-items: center;
        }
        .ant-tabs-tab .anticon {
          margin-right: 8px;
        }
      `}</style>
    </ConfigProvider>
  );
} 