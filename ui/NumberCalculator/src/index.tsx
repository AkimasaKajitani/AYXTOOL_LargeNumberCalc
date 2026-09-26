import React, { useContext, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { AyxAppWrapper, Box, TextField } from '@alteryx/ui';
import { Context as UiSdkContext, DesignerApi } from '@alteryx/react-comms';

const operators = [
  { value: '+', label: 'Add (+)' },
  { value: '-', label: 'Subtract (-)' },
  { value: '*', label: 'Multiply (*)' },
  { value: '/', label: 'Divide (/)' },
  { value: '^', label: 'Power (^)' }
];

const getStringFields = (metaFields: any): any[] => {
  if (!Array.isArray(metaFields)) {
    return [];
  }

  return metaFields.reduce((fields, connectionGroup) => {
    const connections = Array.isArray(connectionGroup) ? connectionGroup : [connectionGroup];
    return fields.concat(connections.reduce((groupFields, connection) => {
      const connectionFields = Array.isArray(connection?.fields) ? connection.fields : [];
      return groupFields.concat(connectionFields.filter(field => {
        const type = String(field.type || '').toLowerCase();
        return type.includes('string');
      }));
    }, []));
  }, []);
};

const App = () => {
  const [model, handleUpdateModel] = useContext(UiSdkContext);
  const configuration = model.Configuration || {};
  const fields = getStringFields(model.Meta?.fields);

  const updateConfiguration = (name: string, value: string) => {
    handleUpdateModel({
      ...model,
      Configuration: {
        ...configuration,
        [name]: value
      }
    });
  };

  useEffect(() => {
    handleUpdateModel({
      ...model,
      Configuration: {
        ...configuration,
        operator: configuration.operator || '+',
        resultField: configuration.resultField || 'result'
      }
    })
  }, []);

  return (
    <Box p={4}>
      <Box style={{ display: 'flex', flexDirection: 'column', gap: 24, width: '100%' }}>
        <TextField select fullWidth SelectProps={{ native: true }} inputProps={{ style: { paddingLeft: 12, paddingRight: 12 } }} label="First field" value={configuration.firstField || ''} onChange={event => updateConfiguration('firstField', event.target.value)}>
          <option value="" />
          {fields.map(field => <option key={`first-${field.name}`} value={field.name}>{field.name}</option>)}
        </TextField>
        <TextField select fullWidth SelectProps={{ native: true }} inputProps={{ style: { paddingLeft: 12, paddingRight: 12 } }} label="Second field" value={configuration.secondField || ''} onChange={event => updateConfiguration('secondField', event.target.value)}>
          <option value="" />
          {fields.map(field => <option key={`second-${field.name}`} value={field.name}>{field.name}</option>)}
        </TextField>
        <TextField select fullWidth SelectProps={{ native: true }} inputProps={{ style: { paddingLeft: 12, paddingRight: 12 } }} label="Operator" value={configuration.operator || '+'} onChange={event => updateConfiguration('operator', event.target.value)}>
          {operators.map(operator => <option key={operator.value} value={operator.value}>{operator.label}</option>)}
        </TextField>
        <TextField fullWidth inputProps={{ style: { paddingLeft: 12, paddingRight: 12 } }} label="Result field name" value={configuration.resultField || 'result'} onChange={event => updateConfiguration('resultField', event.target.value)} />
      </Box>
    </Box>
  )
}

const Tool = () => {
  return (
    <DesignerApi messages={{}} defaultConfig={{ Configuration: { firstField: '', secondField: '', operator: '+', resultField: 'result' } }}>
      <AyxAppWrapper>
        <App />
      </AyxAppWrapper>
    </DesignerApi>
  )
}

ReactDOM.render(
  <Tool />,
  document.getElementById('app')
);
