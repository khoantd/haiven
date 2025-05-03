// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Tooltip } from "antd";
import { RiInformationFill } from "react-icons/ri";

const HelpTooltip = ({ text, testid = "" }) => {
  return (
    <span data-testid={testid}>
      <Tooltip
        classNames={{ root: "tooltip-help" }}
        color="#003d4f"
        placement="bottom"
        title={text}
      >
        <>
          <RiInformationFill />
        </>
      </Tooltip>
    </span>
  );
};

export default HelpTooltip;
