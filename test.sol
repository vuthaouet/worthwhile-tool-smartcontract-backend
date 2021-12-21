Tool & RuleId & Vulnerability & Type
  & Call data forwarded with delegatecall() & AccessControl \\ \hline
  & DELEGATECALL to a user-supplied address & AccessControl \\ \hline
  & Dependence on predictable environment variable & Other \\ \hline
  & Dependence on predictable variable & Other \\ \hline
  & Ether send & AccessControl  \\ \hline
  & Exception state & Other \\ \hline
  & Integer Overflow & Arithmetic \\ \hline
  & Integer Underflow & Arithmetic \\ \hline
  & Message call to external contract & Reentrancy \\ \hline
  & Multiple Calls & Ignore \\ \hline
  & State change after external call & Reentrancy \\ \hline
  & Transaction order dependence & FrontRunning   \\ \hline
  & Unchecked CALL return value & UncheckedLowCalls \\ \hline
  & Unchecked SUICIDE & AccessControl \\ \hline
  & Use of tx.origin & AccessControl   \\ \hline
oyente & DenialService\_2 & Callstack Depth Attack Vulnerability. & DenialService \\ \hline
oyente & Arithmetic\_11 & Integer Overflow. & Arithmetic \\ \hline
oyente & Arithmetic\_12 & Integer Underflow. & Arithmetic \\ \hline
oyente & AccessControl\_16 & Parity Multisig Bug 2. & AccessControl \\ \hline
oyente & Reentrancy\_6 & Re-Entrancy Vulnerability. & Reentrancy   \\ \hline
oyente & TimeManipulation\_3 & Timestamp Dependency. & TimeManipulation \\ \hline
slither & AccessControl\_19 & arbitrary-send & AccessControl \\ \hline
slither & Ignore\_5 & assembly & Ignore \\ \hline
slither & DenialService\_3 & calls-loop & DenialService  \\ \hline
slither & Ignore\_6 & constable-states & Ignore  \\ \hline
slither & Ignore\_7 & constant-function & Ignore  \\ \hline
slither & AccessControl\_20 & controlled-delegatecall & AccessControl \\ \hline
slither & Ignore\_8 & deprecated-standards & Ignore \\ \hline
slither & Ignore\_9 & erc20-indexed & Ignore        \\ \hline
slither & Ignore\_10 & erc20-interface & Ignore     \\ \hline
slither & Ignore\_11 & external-function & Ignore   \\ \hline
slither & Other\_11 & incorrect-equality & Other    \\ \hline
slither & Other\_12 & locked-ether & Other          \\ \hline
slither & UncheckedLowCalls\_5 & low-level-calls & UncheckedLowCalls  \\ \hline
slither & Ignore\_12 & naming-convention & Ignore         \\ \hline
slither & Reentrancy\_9 & reentrancy-benign & Reentrancy  \\ \hline
slither & Reentrancy\_10 & reentrancy-eth & Reentrancy    \\ \hline
slither & Reentrancy\_11 & reentrancy-no-eth & Reentrancy \\ \hline
slither & Ignore\_13 & shadowing-abstract & Ignore        \\ \hline
slither & Ignore\_14 & shadowing-builtin & Ignore         \\ \hline
slither & Ignore\_15 & shadowing-local & Ignore           \\ \hline
slither & Ignore\_16 & shadowing-state & Ignore           \\ \hline
slither & Ignore\_17 & solc-version & Ignore                       \\ \hline
slither & AccessControl\_21 & suicidal & AccessControl             \\ \hline
slither & TimeManipulation\_4 & timestamp & TimeManipulation       \\ \hline
slither & AccessControl\_22 & tx-origin & AccessControl            \\ \hline
slither & Other\_13 & uninitialized-local & Other                  \\ \hline
slither & Other\_14 & uninitialized-state & Other                  \\ \hline
slither & Other\_15 & uninitialized-storage & Other                \\ \hline
slither & UncheckedLowCalls\_6 & unused-return & UncheckedLowCalls \\ \hline
slither & Ignore\_18 & unused-state & Ignore                   \\ \hline
honeybadger & Ignore\_42 & hidden_state_update & Ignore        \\ \hline
honeybadger & Other\_20 & uninitialised_struct & Other         \\ \hline
honeybadger & Ignore\_43 & inheritance_disorder & Ignore       \\ \hline
honeybadger & Reentrancy\_13 & straw_man_contract & Reentrancy \\ \hline
honeybadger & Other\_21 & hidden_transfer & Other              \\ \hline
honeybadger & Ignore\_44 & balance_disorder & Ignore           \\ \hline
honeybadger & Arithmetic\_18 & type_overflow & Arithmetic      \\ \hline