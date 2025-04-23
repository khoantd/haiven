// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import Link from "next/link";
import {
  RiFlaskLine,
  RiLightbulbLine,
  RiCodeBoxLine,
  RiBookReadLine,
  RiChat2Line,
  RiChatQuoteLine,
  RiCompasses2Line,
  RiBook2Line,
  RiDashboardHorizontalLine,
  RiInformationLine,
} from "react-icons/ri";

// Keeping the implementation of menu items for the "static" features in one place
// Will usually be enhanced by the dynamically loaded prompts afterwards

export const initialiseMenuCategoriesForSidebar = () => {
  return {
    dashboard: {
      key: "dashboard",
      label: <Link href="/">Dashboard</Link>,
      icon: <RiDashboardHorizontalLine style={{ fontSize: "large" }} />,
    },
    // about: {
    //   key: "about",
    //   label: <Link href="/boba/about">About</Link>,
    //   icon: <RiInformationLine style={{ fontSize: "large" }} />,
    // },
    knowledgeChat: {
      key: "knowledgeChat",
      label: <Link href="/knowledge-chat">Chat with Haiven</Link>,
      icon: <RiChatQuoteLine style={{ fontSize: "large" }} />,
    },
    research: {
      key: "research",
      label: "Research",
      icon: <RiBook2Line style={{ fontSize: "large" }} />,
      children: [
        {
          key: "company-research",
          label: <Link href="/company-research">Company Research</Link>,
        },
        {
          key: "ai-tool-research",
          label: <Link href="/company-research?config=ai-tool">AI Tool Research</Link>,
        },
        {
          key: "business-strategy",
          label: <Link href="/business-strategy">Business Strategy</Link>,
        },
        {
          key: "strategy-evaluation",
          label: <Link href="/strategy-evaluation">Strategy Evaluation</Link>,
        },
      ],
    },
    ideate: {
      key: "ideate",
      label: "Ideate",
      icon: <RiLightbulbLine style={{ fontSize: "large" }} />,
      children: [
        {
          key: "creative-matrix",
          label: <Link href="/creative-matrix">Creative Matrix</Link>,
        },
        {
          key: "scenarios",
          label: <Link href="/scenarios">Scenario Design</Link>,
        },
      ],
    },
    analysis: {
      key: "analyse",
      label: "Analyse",
      icon: <RiBookReadLine style={{ fontSize: "large" }} />,
      children: [],
    },
    coding: {
      key: "coding",
      label: "Coding",
      icon: <RiCodeBoxLine style={{ fontSize: "large" }} />,
      children: [],
    },
    testing: {
      key: "testing",
      label: "Testing",
      icon: <RiFlaskLine style={{ fontSize: "large" }} />,
      children: [],
    },
    architecture: {
      key: "architecture",
      label: "Architecture",
      icon: <RiCompasses2Line style={{ fontSize: "large" }} />,
      children: [],
    },
    other: {
      key: "other",
      label: "Other",
      icon: <RiChat2Line style={{ fontSize: "large" }} />,
      children: [],
    },
  };
};

export const staticFeaturesForDashboard = () => {
  return [
    {
      identifier: "boba-company-research",
      title: "Company Research",
      help_prompt_description:
        "Research companies and AI tools to understand their business context, competitors, and domain functions.",
      categories: ["research"],
      type: "static",
      link: "/company-research",
    },
    {
      identifier: "boba-ai-tool-research",
      title: "AI Tool Research",
      help_prompt_description:
        "Research AI tools specifically for software delivery teams, including their features, maturity, and market position.",
      categories: ["research"],
      type: "static",
      link: "/company-research?config=ai-tool",
    },
    {
      identifier: "boba-business-strategy",
      title: "Business Strategy",
      help_prompt_description:
        "Develop comprehensive business strategies including market analysis, competitive positioning, and growth plans.",
      categories: ["research"],
      type: "static",
      link: "/business-strategy",
    },
    {
      identifier: "boba-strategy-evaluation",
      title: "Strategy Evaluation",
      help_prompt_description:
        "Evaluate business strategies using frameworks like SWOT/TOWS, Value Chain, 5 Forces Analysis, and Comparative Advantage.",
      categories: ["research"],
      type: "static",
      link: "/strategy-evaluation",
    },
    {
      identifier: "boba-creative-matrix",
      title: "Creative Matrix",
      help_prompt_description:
        'Create a "Creative Matrix" to generate new ideas across dimensions that you can define yourself.',
      categories: ["ideate"],
      type: "static",
      link: "/creative-matrix",
    },
    {
      identifier: "boba-scenarios",
      title: "Scenario Design",
      help_prompt_description:
        "Brainstorm a range of scenarios for your product domain based on criteria like time horizon, realism, and optimism.",
      categories: ["ideate"],
      type: "static",
      link: "/scenarios",
    },
  ];
};
