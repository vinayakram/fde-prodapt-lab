# Lab 3: AI Review (Frontend)

In this lab, we will integrate the frontend with the new API that we have built.

Old workflow:

1. User fills add job form
1. Submit to add job API
1. Job added

New workflow:

1. User fills add job form
1. Submit to review description API
1. Display review comments in the form
1. User can edit job description and submit again
1. Submit to add job API
1. Job added

Notice how our page has two states. In the beginning, submit of form will go to the review API. After that the second submit will go to the Add Job API.

Also, first time there will be no review comments displayed, but after first submit the page has to be updated with the review comments.

We will use `useState` feature of React to track both of these.

Here are the steps to complete the lab:

1. Create state variables to store the reviewed state and the review summary from the API
1. Add the reviewed state as hidden field to the form
1. Update `clientAction` code to check the reviewed state
    * If not yet reviewed, call review API and return response json
    * If reviewed, call add job API and redirect to job board
1. Update the component logic
    * If `actionData` is present, update the reviewed state and review summary state
    * Display the summary in the form if it is present
    * Change the submit button to show `Review` first, then `Submit` after review

## High level approach

1. First, we change the button on the form so that it is called `Review` instead of `Submit`. Change the endpoint url used in `clientAction` so that it goes to the review job description API. Update the return value to return `response.json()` instead of redirecting. This value will be available in component in `actionData` variable. Open developer tools and check that API call is going to the right place
1. Create a state variable `reviewed` (initial value `false`) to store whether the review is completed or not, also another state variable `summary` (initial value empty string) to store the review comments from the backend
1. Add the value of the `reviewed` variable as a hidden field so that the `clientAction` can access it. Reload the page and verify that the hidden field is present with the correct value.

Now we have to implement the logic for two states

1. Update `NewJobBoardForm` component. If `actionData` is available, then we need to update the state variables. Set `reviewed` to `true` and set `summary` to `actionData.overall_summary`. Reload page. Open developer tools and check - first submit makes call to review API, second submit makes call to add jobs API
1. Add a code to the form to display the value of `overall_summary` state. Reload and test that the summary is getting shown after review
1. Update the Submit button so that it says `Review` first and then `Submit` after submission. Reload page and test.
1. Update `clientAction` to read the value of `reviewed` state. If the state is `false` then the `clientAction` should post to the review api and return the json response (current behaviour). If the state is `true` then it should post to add job API and redirect the page after that (old behaviour).

## Hints

### How do I create the states?

<details>
<summary>Hint</summary>

Use `useState` in the component, two times: once for reviewed state and once for the summary
</details>

<details>
<summary>Answer</summary>

```jsx
  const [reviewed, setReviewed] = useState("false")
  const [summary, setSummary] = useState("")
```
</details>

### How do I add reviewed state in the form?

<details>
<summary>Hint</summary>

Same way how you added `job_board_id`
</details>

<details>
<summary>Answer</summary>

```jsx
<input type="hidden" name="reviewed" value={reviewed} />
```
</details>

### How do I make clientData use the review API?

<details>
<summary>Answer</summary>

```jsx
    const response = await fetch('/api/review-job-description', {
      method: 'POST',
      body: formData
    })
    return response.json();
```
</details>

### How do I update the state after the form is submitted?

<details>
<summary>Answer</summary>

Put this in the component after `useState` definitions

```jsx
  if (actionData && reviewed === "false") {
    setSummary(actionData.overall_summary);
    setReviewed("true")
  }
```
</details>

### How do I change which button (Review or Submit) is displayed?

<details>
<summary>Answer</summary>

```jsx
{reviewed === "false" ? <Button type="submit">Review</Button>: <Button type="submit">Submit</Button>}
```

### How do I display the review summary?

<details>
<summary>Answer</summary>

```jsx
          {reviewed === "true" ? (
            <p>{summary}</p>
          ) : <div></div>}
```
</details>

### How do I make clientAction switch the API being called?

<details>
<summary>Answer</summary>

```jsx
export async function clientAction({ request }: Route.ClientActionArgs) {
  const formData = await request.formData()
  const reviewed = formData.get('reviewed')
  const job_board_id = parseInt(formData.get('job_board_id'))
  if (reviewed === "true") {
    await fetch('/api/job-posts', {
      method: 'POST',
      body: formData
    })
    return redirect(`/job-boards/${job_board_id}/job-posts`);
  } else {
    const response = await fetch('/api/review-job-description', {
      method: 'POST',
      body: formData
    })
    return response.json();
  }
}
```

## Discussion Questions

1. Is there a better way to test this code than loading page in browser and checking developer console every time?
