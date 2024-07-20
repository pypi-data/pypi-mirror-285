use crate::model::StateViewMut;

mod any;
mod noop;
mod periodic;
mod zero;

pub use any::AnyBoundary;
pub use noop::NoopBoundary;
pub use periodic::PeriodicBoundary;
pub use zero::ZeroBoundary;

pub trait BoundaryCondition<S: ?Sized + StateViewMut> {
    fn apply(&mut self, state: &mut S);
}
