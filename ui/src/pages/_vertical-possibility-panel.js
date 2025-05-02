// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Button, Flex } from "antd";
import { RiLightbulbLine } from "react-icons/ri";

const VerticalPossibilityPanel = ({ scenarioQueries = [], onClick }) => {
  return (
    <Flex
      marginBottom="1em"
      style={{ width: "100%" }}
      className="suggestions-list"
    >
      <Flex align="flex-start" gap="small" vertical style={{ width: "100%" }}>
        <div className="suggestions-title">Suggestions:</div>
        {scenarioQueries.map((text, i) => (
          <Button
            key={i}
            onClick={() => {
              onClick(text.description);
            }}
            className="suggestion"
          >
            <RiLightbulbLine />
            {text.name}
          </Button>
        ))}
      </Flex>
    </Flex>
  );
};

export default VerticalPossibilityPanel;
