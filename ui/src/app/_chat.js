// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { ActionIconGroup, ProChat, useProChat } from "@ant-design/pro-chat";
import { useTheme } from "antd-style";
import { Button, Collapse, Form, Input, Modal } from "antd";
import { UpOutlined } from "@ant-design/icons";
import { PinIcon, RotateCw, Trash, Copy, Edit } from "lucide-react";
import {
  RiSendPlane2Line,
  RiStopCircleFill,
  RiAttachment2,
} from "react-icons/ri";
import React, {
  forwardRef,
  useImperativeHandle,
  useState,
  useRef,
  useEffect,
} from "react";
import MarkdownRenderer from "./_markdown_renderer";
import { addToPinboard } from "./_local_store";
import { toast } from "react-toastify";

const ChatWidget = forwardRef(
  (
    {
      onSubmitMessage,
      helloMessage,
      placeholder,
      promptPreviewComponent,
      advancedPromptingMenu,
      conversationStarted,
    },
    ref,
  ) => {
    const proChat = useProChat();
    const [form] = Form.useForm();
    const textAreaRef = useRef(null);

    const [isLoading, setIsLoading] = useState(false);
    const [prompt, setPrompt] = useState("");
    const [isPromptOptionsMenuExpanded, setPromptOptionsMenuExpanded] =
      useState(false);
    const [isEditModalVisible, setIsEditModalVisible] = useState(false);
    const [editingMessage, setEditingMessage] = useState({
      id: null,
      content: "",
    });

    // Restore focus to input after response completes
    useEffect(() => {
      if (!isLoading && conversationStarted && textAreaRef.current) {
        // Use a small delay to ensure the DOM has fully updated
        setTimeout(() => {
          textAreaRef.current?.focus();
        }, 100);
      }
    }, [isLoading, conversationStarted]);

    const pin = {
      icon: () => {
        return <PinIcon data-testid="pin-action" />;
      },
      key: "pin",
      label: "Pin",
      execute: (props) => {
        addToPinboard(props.time, props.message);
      },
    };
    const regenerate = {
      icon: () => {
        return <RotateCw data-testid="regenerate-action" />;
      },
      key: "regenerate",
      label: "Regenerate",
      execute: (props) => {
        proChat.resendMessage(props["data-id"]);
      },
    };
    const del = {
      icon: () => {
        return <Trash data-testid="delete-action" />;
      },
      key: "del",
      label: "Delete",
      execute: (props) => {
        proChat.deleteMessage(props["data-id"]);
      },
    };
    const copy = {
      icon: () => {
        return <Copy data-testid="copy-action" />;
      },
      key: "copy",
      label: "copy",
      execute: (props) => {
        navigator.clipboard.writeText(props.message);
        toast.success("Copy Success");
      },
    };
    const edit = {
      icon: () => {
        return <Edit data-testid="edit-action" />;
      },
      key: "edit",
      label: "Edit",
      execute: (props) => {
        setEditingMessage({
          id: props["data-id"],
          content: props.message,
        });
        setIsEditModalVisible(true);
      },
    };

    const defaultActions = [copy, pin, regenerate, del];

    const theme = useTheme();

    const userProfile = {
      name: "User",
      avatar: "/boba/user-5-fill-dark-blue.svg",
    };

    const onSubmit = async (messages) => {
      console.log("onSubmit");
      return await onSubmitMessage(messages);
    };

    useImperativeHandle(ref, () => ({
      async startNewConversation(message) {
        proChat.clearMessage();
        return await proChat.sendMessage(message);
      },
      prompt,
      setPromptValue: (value) => {
        setPrompt(value);
        form.setFieldsValue({ question: value });
      },
      focusInput: () => {
        textAreaRef.current?.focus();
      },
    }));

    const onClickAdvancedPromptOptions = (e) => {
      setPromptOptionsMenuExpanded(!isPromptOptionsMenuExpanded);
    };

    const handleEditSave = () => {
      const messages = proChat.getChatMessages?.() || [];
      messages.forEach((msg) => {
        if (msg.parentId === editingMessage.id) {
          proChat.deleteMessage(msg.id);
        }
      });

      proChat.setMessageContent(editingMessage.id, editingMessage.content);
      proChat.resendMessage(editingMessage.id);

      setIsEditModalVisible(false);
    };

    const inputAreaRender = (_, onMessageSend) => {
      const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          form.submit();
        }
      };

      const attachMoreContextItems = [
        {
          key: "1",
          label: (
            <div className="advanced-prompting">
              <RiAttachment2 className="advanced-prompting-icon" />{" "}
              <span>Attach more context</span>{" "}
              <UpOutlined
                className="advanced-prompting-collapse-icon"
                rotate={isPromptOptionsMenuExpanded ? 180 : 0}
              />
            </div>
          ),
          children: <>{advancedPromptingMenu}</>,
          extra: promptPreviewComponent,
          showArrow: false,
        },
      ];
      return (
        <div>
          <Form
            onFinish={async (value) => {
              const { question } = value;
              await onMessageSend(question);
              form.resetFields();
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
                ref={textAreaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isLoading}
                placeholder={placeholder || "Type a message..."}
                autoSize={{ minRows: 4, maxRows: 15 }}
                onKeyDown={handleKeyDown}
                data-testid="chat-user-input"
              />
            </Form.Item>
            <Form.Item className="chat-text-area-submit">
              {isLoading ? (
                <Button
                  type="secondary"
                  icon={<RiStopCircleFill fontSize="large" />}
                  onClick={() => proChat.stopGenerateMessage()}
                >
                  STOP
                </Button>
              ) : (
                <Button
                  htmlType="submit"
                  icon={<RiSendPlane2Line fontSize="large" />}
                >
                  SEND
                </Button>
              )}
            </Form.Item>
          </Form>
          {advancedPromptingMenu && !conversationStarted ? (
            <Collapse
              className="prompt-options-menu"
              items={attachMoreContextItems}
              defaultActiveKey={["1"]}
              ghost={isPromptOptionsMenuExpanded}
              activeKey={isPromptOptionsMenuExpanded ? "1" : ""}
              onChange={onClickAdvancedPromptOptions}
              collapsible="header"
            />
          ) : null}
        </div>
      );
    };

    return (
      <>
        <ProChat
          style={{
            height: "100%", // this is important for the chat_exploration styling!
          }}
          showTitle
          assistantMeta={{
            avatar: "/boba/shining-fill-white.svg",
            title: "Haiven",
            backgroundColor: "#003d4f",
          }}
          userMeta={{
            avatar: userProfile.avatar ?? userProfile.name,
            title: userProfile.name,
            backgroundColor: "#47a1ad",
          }}
          locale="en-US"
          helloMessage={helloMessage || "Let me help you with your task!"}
          request={onSubmit}
          chatItemRenderConfig={{
            contentRender: (props, _defaultDom) => {
              if (props.loading) {
                setIsLoading(true);
              } else {
                setIsLoading(false);
              }

              const isError = props.message.startsWith("[ERROR]: ")
                ? props.message.replace("[ERROR]: ", "")
                : null;
              return (
                <div
                  className={`chat-message ${props.primary ? "user" : "assistant"}`}
                >
                  {isError ? (
                    <p style={{ color: "red" }}>{isError}</p>
                  ) : (
                    <MarkdownRenderer content={props.message} />
                  )}
                </div>
              );
            },
            actionsRender: (props, _defaultDom) => {
              const actions = props.primary
                ? [...defaultActions, edit]
                : defaultActions;

              return (
                <ActionIconGroup
                  items={actions}
                  onActionClick={(action) => {
                    action.item.execute(props);
                  }}
                  type="ghost"
                />
              );
            },
          }}
          inputAreaRender={inputAreaRender}
        />
        <Modal
          title="Edit Message"
          open={isEditModalVisible}
          onOk={handleEditSave}
          onCancel={() => setIsEditModalVisible(false)}
          okText="Save"
          cancelText="Cancel"
        >
          <Input.TextArea
            value={editingMessage.content}
            onChange={(e) =>
              setEditingMessage((prev) => ({
                ...prev,
                content: e.target.value,
              }))
            }
            autoSize={{ minRows: 3 }}
          />
        </Modal>
      </>
    );
  },
);

export default ChatWidget;
