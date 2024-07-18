const { useEffect, useState, useRef } = React;

const {
  ThemeProvider, CssBaseline, Button, FormControl, InputLabel, Select, OutlinedInput, MenuItem, Card, CardContent,
  TextField, Grid, CardHeader, Typography, Box, CircularProgress, createTheme, Container, Snackbar, Alert,
} = MaterialUI;

const apiEndpoint = "https://localhost.localstack.cloud:4566/_localstack/resource-graph";

const sleep = ms => new Promise(r => setTimeout(r, ms));

const sendRequest = async (path, request, method) => {
  const url = `${apiEndpoint}${path}`;
  method = method || (request ? "post" : "get");
  request = typeof request !== "string" ? JSON.stringify(request) : request;
  const headers = request ? { "Content-Type": "application/json" } : {};
  const result = await axios[method](url, request, { headers });
  if (result.status >= 400) {
    throw Error(`Invalid API response (${result.status}): ${result.data}`);
  }
  return result.data;
};

const AWS_REGIONS = [
  'us-east-1',
  'us-east-2',
  'us-west-1',
  'us-west-2',
  'ca-central-1',
  'ca-west-1',
  'eu-north-1',
  'eu-west-3',
  'eu-west-2',
  'eu-west-1',
  'eu-central-1',
  'eu-south-1',
  'ap-south-1',
  'ap-northeast-1',
  'ap-northeast-2',
  'ap-northeast-3',
  'ap-southeast-1',
  'ap-southeast-2',
  'ap-southeast-3',
  'ap-southeast-4',
  'ap-east-1',
  'sa-east-1',
  'cn-north-1',
  'cn-northwest-1',
  'us-gov-east-1',
  'us-gov-west-1',
  'me-south-1',
  'af-south-1',
  'me-central-1',
  'eu-south-2',
  'eu-central-2',
  'ap-south-2',
  'il-central-1',
].sort();

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const App = () => {
  const [regions, setRegions] = useState([]);
  const [port, setPort] = useState('4510');
  const [status, setStatus] = useState({ scanning: false, importing: false, error: false });
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState(null);
  const [supportedResources, setSupportedResources] = useState([[], [], [], []]);
  const isFirstRender = useRef(true);

  const statusRef = useRef(status)
  const isLoading = status.scanning || status.importing

  const handleChange = (event) => {
    setRegions(event.target.value)
  };

  const showSnackBar = (message) => {
    setOpen(true);
    setMessage(message);
  }
  const handleClick = () => {
    sendRequest('/import', {
      regions,
      port,
    })
  }
  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (!status.scanning && !status.importing) {
      showSnackBar({
        message: status.error ? 'An error occurred, check container logs for more info' : 'Successfully imported',
        severity: status.error ? 'error' : 'success',
      })
    }
  }, [status.scanning, status.importing]);

  useEffect(() => {
    const getStatus = async () => {
      const result = await sendRequest("/status");
      if (JSON.stringify(result) !== JSON.stringify(statusRef)) {
        setStatus(result);
      }
    };

    const intervalId = setInterval(getStatus, 1000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  useEffect(() => {
    const getSupportedResources = async () => {
      const result = await sendRequest("/supported-resources");
      const resources = [[], [], [], []]
      const columnsLength = Math.ceil(result.resources.length / 4)
      for (let i = 0; i < 4; i++) {
        for (let j = 0; j < columnsLength; j++) {
          resources[i].push(result.resources[i * columnsLength + j])
        }
      }
      setSupportedResources(resources)
    };
    getSupportedResources();
  }, [])

  console.log(supportedResources)
  return (
    <Container maxWidth={'lg'}>
      <Snackbar
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        open={open}
        autoHideDuration={6000}
        onClose={() => setOpen(false)}
      >
        <div>
          <Alert
            onClose={() => setOpen(false)}
            severity={message?.severity}
          >
            {message?.message}
          </Alert>
        </div>
      </Snackbar>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Card sx={{ padding: 2 }}>
            <CardHeader action={
              <Button
                onClick={handleClick}
                variant="contained"
              >
                Import
              </Button>
            }
              title="Resource Graph - LocalStack Extension"
              subheader="This extension allows you to perform a complete scan of resources in your aws account and
         inject it into a neptune cluster to be then visualized from app.localstack.cloud"
            />
            <CardContent>
              {
                isLoading &&
                <Box
                  alignItems="center"
                  fullWidth mb={3}
                  display='flex'
                  flexDirection='row'
                  justifyContent="center"
                  spacing={2}
                >
                  <CircularProgress />
                  {status.scanning ? 'Scanning resources...' : 'Importing resources...'}
                </Box>
              }
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={6} xl={6} >
                      <Typography>
                        The list of regions where to perform the scan. The more the regions, the longer the scan will take;
                        it's suggested to minimize them to the ones currently used
                      </Typography>
                    </Grid>
                    <Grid item xs={6} xl={6}>
                      <FormControl sx={{ m: 1, width: 300 }}>
                        <InputLabel id="multi-region">Regions</InputLabel>
                        <Select
                          labelId="multi-region"
                          multiple
                          value={regions}
                          onChange={handleChange}
                          input={<OutlinedInput label="Regions" />}
                          MenuProps={MenuProps}
                        >
                          {AWS_REGIONS.map((region) => (
                            <MenuItem
                              key={region}
                              value={region}
                            >
                              {region}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                </Grid>
                <Grid item xs={12}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={6} xl={6} >
                      <Typography>
                        The port of the neptune cluster to inject the graph
                      </Typography>
                    </Grid>
                    <Grid item xs={6} xl={6}>
                      <TextField
                        label="Port"
                        sx={{ m: 1, width: '25ch' }}
                        value={port}
                        onChange={(event) => {
                          setPort(event.target.value);
                        }}
                      />
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </CardContent>
          </Card >
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardHeader 
            title="Supported Resource" 
            subheader={
              <>
              The list of all the resources that will be scanned and imported into the graph
              </>
            }
            />
            <CardContent>
              <Box display="flex" flexWrap="wrap" justifyContent="space-between" m={2}>
                {supportedResources.map((group) => (
                  <Box m={2}>
                    <ul key={group.join('')}>
                      {group.map((resource) => (
                        <li key={resource}>
                          {resource}
                        </li>
                      ))}
                    </ul>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const StyledApp = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  );
}

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(React.createElement(StyledApp));