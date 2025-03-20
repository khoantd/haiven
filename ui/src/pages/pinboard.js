// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { Modal, Card, Button, Tooltip, Tabs } from "antd";
import {
  RiDeleteBinLine,
  RiCheckboxMultipleBlankFill,
  RiAddBoxLine,
  RiPushpinLine,
} from "react-icons/ri";
import { ClockIcon } from "lucide-react";
import { toast } from "react-toastify";
import {
  getPinboardData,
  getSortedUserContexts,
  deleteContextByTimestamp,
  deletePinOrNoteByTimestamp,
} from "../app/_local_store";
import MarkdownRenderer from "../app/_markdown_renderer";
import AddNewNote from "../app/_add_new_note";
import AddContext from "../app/_add_context";

const Pinboard = ({ isModalVisible, onClose }) => {
  const [isMounted, setIsMounted] = useState(false);
  const [pinnedMessages, setPinnedMessages] = useState([]);
  const [savedUserContexts, setSavedUserContexts] = useState([]);
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [isAddingContext, setIsAddingContext] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    setIsMounted(true);
    const loadData = () => {
      try {
        setPinnedMessages(getPinboardData() || []);
        setSavedUserContexts(getSortedUserContexts() || []);
      } catch (error) {
        console.error('Error loading pinboard data:', error);
        setPinnedMessages([]);
        setSavedUserContexts([]);
      }
    };
    
    loadData();
    
    // Listen for storage changes
    const handleStorageChange = (e) => {
      if (e.key === 'pinboard' || e.key === 'context') {
        loadData();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Server-side render a loading state or nothing
  if (typeof window === 'undefined' || !isMounted) {
    return null;
  }

  const deleteContext = (context) => {
    deleteContextByTimestamp(context.timestamp);
    reloadPinboard();
    toast.success("Content deleted successfully!");
  };

  const deletePinOrNote = (content) => {
    deletePinOrNoteByTimestamp(content.timestamp);
    reloadPinboard();
    toast.success("Content deleted successfully!");
  };

  const copyContent = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
      toast.success("Content copied successfully!");
    } catch (err) {
      toast.error("Failed to copy the context.");
    }
  };
  const copyContext = async (context) => {
    copyContent(contextAsText(context));
  };

  const copyPinOrNote = async (content) => {
    copyContent(content.summary);
  };

  const addNoteButtonWithTooltip = () => {
    const tooltipText = "Add your own reusable text notes to the pinboard";
    return (
      <Tooltip title={tooltipText}>
        <Button
          type="link"
          className="copy-all"
          onClick={() => setIsAddingNote(true)}
        >
          <RiAddBoxLine fontSize="large" /> ADD NOTE
        </Button>
      </Tooltip>
    );
  };

  const addContextButtonWithTooltip = () => {
    const tooltipText =
      "Add your project context to be reused in your Haiven inputs. This will be included in the context dropdown.";
    return (
      <Tooltip title={tooltipText}>
        <Button
          type="link"
          className="copy-all"
          onClick={() => setIsAddingContext(true)}
        >
          <RiAddBoxLine fontSize="large" /> ADD CONTEXT
        </Button>
      </Tooltip>
    );
  };

  function formatDate(timestamp) {
    try {
      const date = new Date(parseInt(timestamp));
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }

      // Use Intl.DateTimeFormat for consistent formatting
      const formatter = new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });

      const formatted = formatter.format(date);
      const dayNum = date.getDate();
      
      // Add suffix
      let suffix = 'th';
      if (dayNum % 10 === 1 && dayNum !== 11) suffix = 'st';
      else if (dayNum % 10 === 2 && dayNum !== 12) suffix = 'nd';
      else if (dayNum % 10 === 3 && dayNum !== 13) suffix = 'rd';

      // Replace the day number with the suffixed version
      return formatted.replace(/\d+/, dayNum + suffix);
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Invalid date';
    }
  }

  const contextAsText = (context) => {
    return "# " + context.title + "\n\n" + context.summary;
  };

  const reloadPinnedMessages = () => {
    setPinnedMessages(getPinboardData());
  };

  const reloadUserSavedContexts = () => {
    setSavedUserContexts(getSortedUserContexts());
  };

  const reloadPinboard = () => {
    reloadPinnedMessages();
    reloadUserSavedContexts();
  };

  const renderContents = (contents, type) => {
    let testid, emptyMessage, copyFunction, deleteFunction, contentToDisplay;
    if (type === "pin-notes") {
      testid = "pin-and-notes-tab";
      emptyMessage =
        "Start pinning by clicking on the pin icon on the messages OR Add your own reusable text notes by clicking on the ADD NOTE button.";
      copyFunction = copyPinOrNote;
      deleteFunction = deletePinOrNote;
      contentToDisplay = (content) => content.summary;
    } else if (type === "contexts") {
      testid = "contexts-tab";
      emptyMessage = "Create context by clicking on the ADD CONTEXT button";
      copyFunction = copyContext;
      deleteFunction = deleteContext;
      contentToDisplay = contextAsText;
    }

    return (
      <div className="pinboard-tab" data-testid={testid}>
        {contents.length === 0 && (
          <div className="empty-pinboard-tab">
            <p className="empty-state-message">{emptyMessage}</p>
          </div>
        )}
        {contents.map((content, i) => (
          <Card
            hoverable
            key={i}
            className={`pinboard-card ${content.isUserDefined ? "user-defined" : ""}`}
            actions={[
              <div
                className="pinboard-card-action-items"
                style={{ backgroundColor: "#f9f9f9" }}
              >
                <div className="card-action">
                  <ClockIcon size={16} className="clock-icon" />
                  {formatDate(content.timestamp)}
                </div>
                <div className="card-action" key="actions">
                  <Button
                    type="link"
                    onClick={() => deleteFunction(content)}
                    data-testid="delete"
                  >
                    <RiDeleteBinLine style={{ fontSize: "large" }} />
                  </Button>
                  <Button
                    type="link"
                    onClick={() => copyFunction(content)}
                    data-testid="copy"
                  >
                    <RiCheckboxMultipleBlankFill
                      style={{ fontSize: "large" }}
                    />
                  </Button>
                </div>
              </div>,
            ]}
          >
            <div className="pinboard-card-content">
              <MarkdownRenderer content={contentToDisplay(content)} />
            </div>
          </Card>
        ))}
      </div>
    );
  };

  const pinAndNotesTab = {
    key: "notes",
    label: (
      <div className="tab-title">
        <h3>Pins/Notes</h3>
      </div>
    ),
    children: renderContents(pinnedMessages, "pin-notes"),
  };

  const contextTab = {
    key: "context",
    label: (
      <div className="tab-title">
        <h3>Contexts</h3>
      </div>
    ),
    children: renderContents(savedUserContexts, "contexts"),
  };

  const tabs = [contextTab, pinAndNotesTab];

  const pinboardHeader = () => {
    return (
      <div className="pinboard-header">
        <div className="pinboard-title">
          <RiPushpinLine fontSize="large" />
          Pinboard
        </div>
        <p className="saved-response">
          Access content you've pinned to reuse in your Haiven inputs.
        </p>
        <div className="pinboard-actions">
          {addContextButtonWithTooltip()}
          {addNoteButtonWithTooltip()}
        </div>
      </div>
    );
  };

  return (
    <Modal
      title={pinboardHeader()}
      open={isModalVisible}
      onCancel={onClose}
      width={420}
      footer={null}
      className="pinboard-modal"
      mask={false}
    >
      <AddNewNote
        isAddingNote={isAddingNote}
        setIsAddingNote={setIsAddingNote}
        reloadData={reloadPinnedMessages}
      />
      <AddContext
        isAddingContext={isAddingContext}
        setIsAddingContext={setIsAddingContext}
        reloadData={reloadUserSavedContexts}
      />
      <Tabs defaultActiveKey="context" items={tabs}></Tabs>
    </Modal>
  );
};

export default Pinboard;
