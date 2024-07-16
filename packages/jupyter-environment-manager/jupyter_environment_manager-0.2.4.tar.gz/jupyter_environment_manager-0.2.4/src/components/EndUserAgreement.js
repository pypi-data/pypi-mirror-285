import { List, ListItem, Stack, Typography } from '@mui/material';
import React from 'react';

const EndUserAgreement = () => {
  return (
    <Stack
      maxHeight={500}
      gap="14px"
      overflow="hidden"
      bgcolor="var(--jp-layout-color2)"
      pl="14px"
      pt="14px"
      borderRadius={2}
      sx={{ overflowY: 'scroll' }}
    >
      <Typography fontSize={14}>
        LICENSE. qBraid is authorized by Intel® Corporation ("Intel") to enable
        qBraid Customers to access Intel's Software in binary form, (with the
        accompanying documentation, the "Software") solely from qBraid's servers
        for the internal use of the qBraid Customer, subject to the following
        conditions:
      </Typography>
      <List sx={{ pt: 0, pb: 0 }}>
        <ListItem>
          <Typography fontSize={14}>
            (a) qBraid Customer may not disclose, distribute or transfer any
            part of the Software except as provided in this Agreement, and
            qBraid Customer agrees to prevent unauthorized copying of the
            Software.
          </Typography>
        </ListItem>
        <ListItem>
          <Typography fontSize={14}>
            (b) qBraid Customer may not reverse engineer, decompile, or
            disassemble the Software.
          </Typography>
        </ListItem>
        <ListItem>
          <Typography fontSize={14}>
            (c) qBraid Customer may not sublicense the Software.
          </Typography>
        </ListItem>
        <ListItem>
          <Typography fontSize={14}>
            (d) The Software may contain the software and other property of
            third-party suppliers, some of which may be identified in, and
            licensed in accordance with, an enclosed license.txt file or other
            text or file.
          </Typography>
        </ListItem>
        <ListItem>
          <Typography fontSize={14}>
            (e) Intel has no obligation to provide any support, technical
            assistance or updates for the Software.
          </Typography>
        </ListItem>
      </List>
      <Typography fontSize={14}>
        OWNERSHIP OF SOFTWARE AND COPYRIGHTS. Title to all copies of the
        Software remains with Intel or its suppliers. The Software is
        copyrighted and protected by the laws of the United States and other
        countries, and international treaty provisions. qBraid Customer may not
        remove any copyright notices from the Software. Except as otherwise
        expressly provided above, Intel grants no express or implied right under
        Intel patents, copyrights, trademarks, or other intellectual property
        rights. Transfer of the license terminates qBraid Customer's right to
        use the Software.
      </Typography>
      <Typography fontSize={14}>
        DISCLAIMER OF WARRANTY. The Software is provided "AS IS" without
        warranty of any kind, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
        LIMITATION, WARRANTIES OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR
        PURPOSE.
      </Typography>
      <Typography fontSize={14} textTransform="uppercase">
        LIMITATION OF LIABILITY. NEITHER INTEL NOR ITS SUPPLIERS WILL BE LIABLE
        FOR ANY LOSS OF PROFITS, LOSS OF USE, INTERRUPTION OF BUSINESS, OR
        INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES OF ANY KIND
        WHETHER UNDER THIS AGREEMENT OR OTHERWISE, EVEN IF INTEL HAS BEEN
        ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
      </Typography>
      <Typography fontSize={14}>
        LICENSE TO USE COMMENTS AND SUGGESTIONS. This Agreement does NOT
        obligate qBraid Customer to provide Intel with comments or suggestions
        regarding the Software. However, if the qBraid Customer provides Intel
        with comments or suggestions for the modification, correction,
        improvement or enhancement of (a) the Software or (b) Intel products or
        processes that work with the Software, qBraid Customer grants to Intel a
        non-exclusive, worldwide, perpetual, irrevocable, transferable,
        royalty-free license, with the right to sublicense, under qBraid's
        Customer's intellectual property rights, to incorporate or otherwise
        utilize those comments and suggestions.
      </Typography>
      <Typography fontSize={14}>
        TERMINATION OF THIS LICENSE. Intel or the sublicensor may terminate this
        license at any time if You are in breach of any of its terms or
        conditions. Upon termination, qBraid Customer will immediately destroy
        the Software, and return to Intel all copies of the Software. THIRD
        PARTY BENEFICIARY. Intel is an intended beneficiary of the End User
        License Agreement and has the right to enforce all of its terms.
      </Typography>
      <Typography fontSize={14}>
        U.S. GOVERNMENT RESTRICTED RIGHTS. No Government procurement regulation
        or contract clauses or provision will be considered a part of any
        transaction between the Parties under this Agreement unless its
        inclusion is required by statute, or mutually agreed upon in writing by
        the Parties in connection with a specific transaction. The technical
        data and computer software covered by this license is a "Commercial
        Item," as that term is defined by the FAR 2.101 (48 C.F.R. 2.101) and is
        “commercial computer software” and "commercial computer software
        documentation" as specified under FAR 12.212 (48 C.F.R. 12.212) or DFARS
        227.7202 (48 C.F.R. 227.7202), as applicable. This commercial computer
        software and related documentation is provided to end users for use by
        and on behalf of the U.S. Government, with only those rights as are
        granted to all other end users under the terms and conditions in this
        Agreement. Use for or on behalf of the U.S. Government is permitted only
        if the party acquiring or using this Software is properly authorized by
        an appropriate U.S. Government official. This use by or for the U.S.
        Government clause is in lieu of, and supersedes, any other FAR, DFARS,
        or other provision that addresses Government rights in the computer
        Software or documentation covered by this license. All copyright
        licenses granted to the U.S. Government are coextensive with the
        technical data and computer Software licenses granted in this Agreement.
        The U.S. Government will only have the right to reproduce, distribute,
        perform, display, and prepare Derivative Works as needed to implement
        those rights.
      </Typography>
      <Typography fontSize={14}>
        EXPORT LAWS. The Software and all related technical information or
        materials are subject to export controls and (are or may be) licensable
        under U.S. Government export regulations. qBraid Customer will not
        export, re-export, divert, transfer or disclose, directly or indirectly,
        the Software, Documentation and any related technical information or
        materials without complying strictly with all legal requirements
        including, without limitation, obtaining the prior approval of the U.S.
        Department of Commerce and, if necessary, other agencies or departments
        of the U.S. Government. Upon request, Intel will provide qBraid Customer
        with information regarding the export classification of the Software
        that may be necessary to assist qBraid Customer's compliance with this
        provision. qBraid Customer will execute and deliver to Intel “Letters of
        Assurance,” confirming compliance with applicable export regulations.
        qBraid Customer will indemnify Intel against any loss related to qBraid
        Customer's failure to conform to these requirements.
      </Typography>
      <Typography fontSize={14}>
        APPLICABLE LAWS. This Agreement is governed by the laws of the state of
        Delaware, excluding its principles of conflict of laws and the United
        Nations Convention on Contracts for the Sale of Goods. qBraid Customer
        may not export the Software in violation of applicable export laws and
        regulations.
      </Typography>
      <Typography fontSize={14}>
        qBraid Customer's specific rights may vary from country to country.
      </Typography>
    </Stack>
  );
};

export default EndUserAgreement;
