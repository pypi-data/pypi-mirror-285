import React from 'react';
import { SVGProps } from 'react';

const WhiteCube = (props: SVGProps<SVGSVGElement>) => {
  return (
    <svg
      width={props.width}
      height={props.height}
      style={{
        minHeight: props.height,
        minWidth: props.width,
        filter: props.filter
      }}
      viewBox="0 0 37.5 35.624999"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g transform="translate(-592.72335,-420.20756)">
        <g transform="matrix(0.5935466,0,0,0.59354645,250.33305,172.30823)">
          <g transform="translate(-67.857146,-23.035712)">
            <path
              fill="#f3f3f0"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 660.75803,449.15562 15.55544,5.66172 15.78565,-5.74552 -15.55544,-5.66172 z"
            />
            <path
              fill="#ffffff"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 676.31347,454.81734 v 18.28268 l 15.78565,-5.74551 v -18.28269 z"
            />
            <path
              fill="#e7e6e2"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 660.75803,449.15562 15.55544,5.66172 v 18.28268 l -15.55544,-5.66171 z"
            />
          </g>
          <g transform="translate(-83.545471,1.0197198)">
            <path
              fill="#f3f3f0"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 660.75803,449.15562 15.55544,5.66172 15.78565,-5.74552 -15.55544,-5.66172 z"
            />
            <path
              fill="#ffffff"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 676.31347,454.81734 v 18.28268 l 15.78565,-5.74551 v -18.28269 z"
            />
            <path
              id="path271"
              fill="#e7e6e2"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 660.75803,449.15562 15.55544,5.66172 v 18.28268 l -15.55544,-5.66171 z"
            />
          </g>
          <g transform="translate(-52.377998,1.0197198)">
            <path
              fill="#f3f3f0"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 660.75803,449.15562 15.55544,5.66172 15.78565,-5.74552 -15.55544,-5.66172 z"
            />
            <path
              fill="#ffffff"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 676.31347,454.81734 v 18.28268 l 15.78565,-5.74551 v -18.28269 z"
            />
            <path
              fill="#e7e6e2"
              fillOpacity="1"
              stroke="#c4c4c4"
              strokeWidth="0.355076"
              strokeLinejoin="bevel"
              strokeMiterlimit="4"
              d="m 660.75803,449.15562 15.55544,5.66172 v 18.28268 l -15.55544,-5.66171 z"
            />
          </g>
        </g>
      </g>
    </svg>
  );
};

WhiteCube.defaultProps = {
  width: '34',
  height: '36',
  filter: 'none'
};

export default WhiteCube;
