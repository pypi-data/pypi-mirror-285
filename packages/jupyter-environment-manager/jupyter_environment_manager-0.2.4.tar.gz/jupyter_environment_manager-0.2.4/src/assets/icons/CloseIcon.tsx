import * as React from 'react';
import { SVGProps } from 'react';

const CloseIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    width={52}
    height={52}
    fill={props.color}
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <circle cx={26.5} cy={26.5} r={14.5} fill="#fff" />
    <path
      d="M26 3.25C13.437 3.25 3.25 13.437 3.25 26S13.437 48.75 26 48.75 48.75 38.563 48.75 26 38.563 3.25 26 3.25Zm8.4 31.393-3.352-.015L26 28.61l-5.043 6.013-3.356.015a.404.404 0 0 1-.406-.406c0-.097.035-.188.096-.264l6.607-7.872-6.607-7.866a.407.407 0 0 1 .31-.67l3.356.015L26 23.593l5.043-6.012 3.351-.016c.224 0 .406.178.406.406a.422.422 0 0 1-.096.264l-6.597 7.867 6.602 7.87a.407.407 0 0 1-.31.67Z"
      fill="#FF5C5C"
    />
  </svg>
);

CloseIcon.defaultProps = {
  color: 'none'
};

export default CloseIcon;
