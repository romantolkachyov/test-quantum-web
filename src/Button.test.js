import {render, screen} from '@testing-library/react'
import '@testing-library/jest-dom'
import Button from './Button'
import {
  MemoryRouter,
  Route,
  Routes
} from "react-router-dom";
import React from "react";

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

export const renderInRouter = (Comp) =>
  render(
    <MemoryRouter>
        <Routes>
            <Route path="*" element={Comp}/>
        </Routes>
    </MemoryRouter>
  );

test('display active button', async () => {
  renderInRouter(<Button data-testid="myButton" state="active" />)
  const el = await screen.findByTestId("myButton")
  expect(el).toHaveTextContent("Start")
})
