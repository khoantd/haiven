// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Button, Flex } from "antd";
import { RiLightbulbLine } from "react-icons/ri";

const HorizontalPossibilityPanel = ({
  scenarioQueries = [],
  disable = false,
  onClick,
}) => {
  return (
    <div>
      <div className="suggestions-title">Suggestions:</div>
      <Flex
        marginBottom="1em"
        style={{ width: "100%" }}
        className="suggestions-list"
      >
        <Flex align="flex-start" gap="small" style={{ width: "100%" }}>
          {scenarioQueries.map((text, i) => (
            <Button
              disabled={disable}
              key={i}
              onClick={() => {
                onClick(text.description);
              }}
              className="horizontal-suggestion"
            >
              <RiLightbulbLine />
              <span className={"suggestions-description"}>{text.name}</span>
            </Button>
          ))}
        </Flex>
      </Flex>
    </div>
  );
};

export default HorizontalPossibilityPanel;
