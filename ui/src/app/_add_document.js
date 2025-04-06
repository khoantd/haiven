// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import AddUserContent from "./_add_user_content";
import { saveDocument } from "./_local_store";

function AddDocument({ isAddingDocument, setIsAddingDocument }) {
  const handleSubmit = (title, description) => {
    saveDocument(title, description);
    setIsAddingDocument(false);
  };

  return (
    <AddUserContent
      isOpen={isAddingDocument}
      setIsOpen={setIsAddingDocument}
      onSubmit={handleSubmit}
      title="Add Document"
      descriptionPlaceholder="Enter document content..."
    />
  );
}

export default AddDocument; 