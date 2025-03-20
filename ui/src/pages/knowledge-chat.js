// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import PromptChat from "../app/_prompt_chat";
import { getInspirationById } from "../app/_boba_api";

const KnowledgeChatPage = ({ prompts, documents, models }) => {
  const [promptId, setPromptId] = useState(null);
  const [initialInput, setInitialInput] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const searchParams = useSearchParams();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const promptParam = searchParams.get("prompt");
    const inspirationId = searchParams.get("inspiration");
    
    setPromptId(promptParam);
    
    if (inspirationId) {
      getInspirationById(inspirationId, (inspiration) => {
        setInitialInput(inspiration.prompt_template || '');
        setIsLoading(false);
      }).catch((error) => {
        console.error("Error loading inspiration:", error);
        setIsLoading(false);
      });
    } else {
      setIsLoading(false);
    }
  }, [searchParams]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <PromptChat
      key={promptId}
      promptId={promptId}
      initialInput={initialInput}
      prompts={prompts || []}
      documents={documents || []}
      models={models || []}
      showTextSnippets={false}
      showImageDescription={true}
      pageTitle="Chat with Haiven"
      pageIntro="Ask anything! You can also upload a document and ask questions about its content."
      headerTooltip={false}
      inputTooltip={false}
    />
  );
};

export default KnowledgeChatPage;
