// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Select, Tooltip, Button } from "antd";
import { RiAddBoxLine } from "react-icons/ri";
import HelpTooltip from "./_help_tooltip";
import AddDocument from "./_add_document";

function DocumentChoice({ documents, onChange }) {
  const [isAddingDocument, setIsAddingDocument] = useState(false);

  const tooltipMessage =
    documents.length === 1
      ? "There are no documents configured in the knowledge pack. Documents can provide project-specific information that Haiven can reuse across prompts."
      : "Choose a document from your knowledge pack that is relevant to your business strategy.";
  return (
    <div className="user-input">
      <div className="input-document-label">
        <label>
          Select your document
          <HelpTooltip
            text={tooltipMessage}
            testid="document-selection-tooltip"
          />
        </label>
        <Tooltip title="Add your project document to be reused in your Haiven inputs. This will be included in the document dropdown.">
          <Button
            type="link"
            className="add-document-icon-button"
            onClick={() => setIsAddingDocument(true)}
          >
            <RiAddBoxLine fontSize="large" />
            Add Document
          </Button>
        </Tooltip>
      </div>

      <Select
        onChange={onChange}
        options={documents}
        defaultValue="base"
        data-testid="document-select"
      />
      <AddDocument
        isAddingDocument={isAddingDocument}
        setIsAddingDocument={setIsAddingDocument}
      />
    </div>
  );
}

export default DocumentChoice; 