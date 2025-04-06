// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
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
  Steps,
  Divider,
  Spin,
  Alert,
  Tooltip,
  Space,
  Select,
} from "antd";
import { 
  RiSendPlane2Line, 
  RiInformationLine, 
  RiFileCopyLine,
  RiDownloadLine,
  RiArrowRightLine
} from "react-icons/ri";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { toast } from "react-toastify";
import useLoader from "../hooks/useLoader";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "../pages/_chat_header";
import { DynamicDataRenderer } from "../app/_dynamic_data_renderer";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export default function CompanyResearchPage() {
  const [researchConfig, setResearchConfig] = useState(null);
  const [companyName, setCompanyName] = useState("");
  const [companyData, setCompanyData] = useState(null);
  const [citations, setCitations] = useState([]);
  const [error, setError] = useState(null);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [disableInput, setDisableInput] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();

  const availableResearchConfig = {
    "company": {
      title: "Company Research",
      key: "company",
      column1: [
        { title: "Business Snapshot", property: "business_brief" },
        { title: "Business Model", property: "business_model_canvas" }
      ],
      column2: [
        { title: "Vision & Strategic Priorities", property: "org_priorities" },
        { title: "Competitors", property: "competitors" },
        { title: "Domain Terms", property: "domain_terms" },
      ],
      column3: [{ title: "Domain Functions", property: "domain_functions" }],
    },
    "ai-tool": {
      title: "AI Tool Research",
      key: "ai-tool",
      column1: [
        { title: "Business Snapshot", property: "business_brief" },
        { title: "Reception", property: "reception" },
      ],
      column2: [
        { title: "Vision & Strategic Priorities", property: "org_priorities" },
        { title: "Competitors", property: "competitors" },
        { title: "Did you know?", property: "other_tidbits" },
      ],
      column3: [
        {
          title: "Software Delivery Lifecycle Support",
          property: "software_lifecycle",
        },
        { title: "Key resources", property: "key_resources" },
      ],
    },
  };

  const searchParams = useSearchParams();

  useEffect(() => {
    const configParam = searchParams.get("config");
    if (configParam && availableResearchConfig[configParam]) {
      setResearchConfig(availableResearchConfig[configParam]);
    } else {
      setResearchConfig(availableResearchConfig.company);
    }
  }, [searchParams]);

  const handleSearch = async (values) => {
    if (!values.companyName.trim()) {
      toast.warning("Please enter a company name");
      return;
    }

    setCompanyName(values.companyName);
    setDisableInput(true);
    setCompanyData(null);
    setCitations([]);
    setError(null);
    setCurrentStep(1);

    const uri = `/api/research`;

    let jsonResponse = "";

    fetchSSE(
      uri,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          userinput: values.companyName, 
          config: researchConfig.key,
          additionalContext: values.additionalContext || ""
        }),
        signal: startLoad(),
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
          } else {
            setCurrentStep(2);
          }
          abortLoad();
        },
        onMessageHandle: (data) => {
          try {
            if (data.data) {
              jsonResponse += data.data;

              // Clean up the response if needed
              jsonResponse = jsonResponse.trim();

              // Try to parse the JSON even if it's incomplete
              try {
                const parsedData = parse(jsonResponse);
                if (parsedData && typeof parsedData === "object") {
                  setCompanyData(parsedData);
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
        <HelpTooltip text="Get a company brief" />
      </h3>
    </div>
  );

  const resetForm = () => {
    form.resetFields();
    setCompanyData(null);
    setCitations([]);
    setError(null);
    setCurrentStep(0);
  };

  const downloadResearch = () => {
    if (!companyData) return;
    
    try {
      // Create a formatted text representation of the research
      let researchText = `# ${companyData.business_brief?.company_name || companyName} Research\n\n`;
      
      // Add each section
      Object.entries(companyData).forEach(([key, value]) => {
        const sectionTitle = key.split('_').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
        
        researchText += `## ${sectionTitle}\n\n${value}\n\n`;
      });
      
      // Add citations if available
      if (citations && citations.length > 0) {
        researchText += `## Sources\n\n`;
        citations.forEach(citation => {
          const url = typeof citation === "string" ? citation : citation.url;
          if (url) {
            researchText += `- ${url}\n`;
          }
        });
      }
      
      const blob = new Blob([researchText], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${companyName.toLowerCase().replace(/\s+/g, '-')}-research-${new Date().toISOString().split('T')[0]}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading research:", error);
      toast.error("Failed to download research. Please try again.");
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
                  const content = companyData?.[item.property];
                  if (content) {
                    navigator.clipboard.writeText(
                      typeof content === 'string' ? content : JSON.stringify(content, null, 2)
                    );
                    toast.success("Copied to clipboard");
                  }
                }}
                className="copy-button"
              />
            </Tooltip>
          </div>
        }
        className="research-card"
        style={{ 
          marginBottom: "16px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
          borderRadius: "8px",
          overflow: "hidden"
        }}
      >
        {Array.isArray(companyData?.[item.property]) ? (
          companyData[item.property].map((listItem, listIndex) => (
            <Card
              key={index + "-" + listIndex}
              size="small"
              className="inner-result"
              style={{ marginBottom: "8px" }}
            >
              <DynamicDataRenderer data={listItem} />
            </Card>
          ))
        ) : (
          <DynamicDataRenderer data={companyData?.[item.property]} />
        )}
      </Card>
    ));
  };

  const Citations = ({ citations }) => {
    if (!citations || !Array.isArray(citations) || citations.length === 0) {
      return null;
    }

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
        <List
          size="small"
          itemLayout="horizontal"
          dataSource={citations}
          style={{ fontSize: "14px" }}
          renderItem={(citation) => {
            // Handle both string URLs and object citations
            const url = typeof citation === "string" ? citation : citation.url;

            if (!url) return null;

            return (
              <List.Item style={{ padding: "4px 0" }}>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: "14px", lineHeight: "1.4" }}
                >
                  {url}
                </a>
              </List.Item>
            );
          }}
        />
      </Card>
    );
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
      <ChatHeader
        models={{ chat: { name: "Perplexity AI" } }}
        titleComponent={title}
      />
      <div className="company-research dashboard">
        <div className="content-container" style={{ padding: "20px" }}>
          <Steps
            current={currentStep}
            items={[
              {
                title: 'Input Details',
                description: 'Provide company information',
              },
              {
                title: 'Researching',
                description: 'Gathering data',
              },
              {
                title: 'Results',
                description: 'View research',
              },
            ]}
            style={{ marginBottom: "24px" }}
          />

          {!disableInput && currentStep === 0 && (
            <div className="research-form-container" style={{ marginBottom: "20px" }}>
              <Card 
                title={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <RiInformationLine style={{ marginRight: '8px' }} />
                    <span>Research Input</span>
                  </div>
                }
                className="research-form-card"
                style={{ 
                  boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
                  borderRadius: "8px",
                  overflow: "hidden"
                }}
              >
                <Form
                  form={form}
                  onFinish={handleSearch}
                  layout="vertical"
                  className="research-form"
                >
                  <Form.Item
                    name="companyName"
                    label="Company Name"
                    rules={[{ required: true, message: "Please enter a company name" }]}
                  >
                    <Input placeholder="Enter company name" />
                  </Form.Item>

                  <Form.Item
                    name="additionalContext"
                    label="Additional Context"
                    tooltip="Add any specific details about the company you want to focus on"
                  >
                    <TextArea
                      rows={4}
                      placeholder="Add any specific context or requirements for the research"
                    />
                  </Form.Item>

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
                      Research Company
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
                Researching {companyName}... This may take a moment.
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

          {companyData && currentStep === 2 && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <Title level={4} style={{ margin: 0 }}>
                  {companyData.business_brief?.company_name || companyName} Research
                </Title>
                <Space>
                  <Button 
                    icon={<RiDownloadLine />} 
                    onClick={downloadResearch}
                    type="primary"
                    style={{ borderRadius: "6px" }}
                  >
                    Download Research
                  </Button>
                  <Button 
                    onClick={resetForm}
                    style={{ borderRadius: "6px" }}
                  >
                    New Research
                  </Button>
                </Space>
              </div>

              <Alert
                message="Research Completed Successfully"
                description="Below is your comprehensive company research. You can copy individual sections or download the entire research."
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
                  {createColumn(researchConfig.column1)}
                </Col>
                <Col xs={24} md={8}>
                  {createColumn(researchConfig.column2)}
                </Col>
                <Col xs={24} md={8}>
                  {createColumn(researchConfig.column3)}
                </Col>
              </Row>

              <Citations citations={citations} />

              <Card 
                title={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <RiInformationLine style={{ marginRight: '8px' }} />
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
                  Now that you have your company research, consider these next steps:
                </Paragraph>
                <ul style={{ fontSize: '16px', lineHeight: '1.6', paddingLeft: '20px' }}>
                  <li style={{ marginBottom: '8px' }}>Use this information to inform your business strategy</li>
                  <li style={{ marginBottom: '8px' }}>Explore our <a href="/boba/business-strategy">Business Strategy</a> tool to develop a strategic plan</li>
                  <li style={{ marginBottom: '8px' }}>Compare this company with competitors using our research tool</li>
                  <li style={{ marginBottom: '8px' }}>Save this research for future reference</li>
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
        .research-card .ant-card-head {
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        .research-card .ant-card-body {
          padding: 16px;
        }
        .citations-card .ant-card-head {
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        .citations-card .ant-card-body {
          padding: 16px;
        }
      `}</style>
    </ConfigProvider>
  );
}
